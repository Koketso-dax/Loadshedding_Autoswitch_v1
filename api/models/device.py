"""
    Python module for Device Table
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Dict, Optional
from sqlalchemy import event, text
from sqlalchemy.orm import mapped_column, relationship, validates, Mapped, query
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from models import db
from models.metric import Metric
from models.user import User


class DeviceStatus(str, Enum):
    """Device operational status"""
    ON = 'on'
    OFF = 'off'
    MAINTENANCE = 'maintenance'
    ERROR = 'error'
    UNKNOWN = 'unknown'

class Device(db.Model):
    """
        Class representation of Devices.
        --------------------------------
        Attributes:
            id: Unique identifier
            device_key: Unique device identifier string
            user_id: Associated user identifier
            status: Current device status
            last_seen: Last time device was active
            metadata: Additional device information
            configuration: Device-specific settings
            metrics: Associated metrics
    """
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(primary_key=True)
    device_key: Mapped[str] = mapped_column(db.String(128), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status: Mapped[str] = mapped_column(db.String(20), default=DeviceStatus.UNKNOWN)
    last_seen: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), 
                                              default=lambda: datetime.now(timezone.utc))
    metadata: Mapped[Dict] = mapped_column(JSONB, default={})
    configuration: Mapped[Dict] = mapped_column(JSONB, default={})

     # Relationships
    user = relationship("User", back_populates="devices")
    metrics: Mapped[List[Metric]] = relationship(
        "Metric",
        back_populates="device",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Validation thresholds
    INACTIVITY_THRESHOLD = timedelta(minutes=30)
    CHANGE_THRESHOLD = 0.1

    def __init__(self, device_key: str, user: User,
                 metadata: Optional[Dict] = None):
        self.device_key = device_key
        self.user = user
        self.metadata = metadata or {}
        self.configuration = self._get_default_configuration()

    @validates('device_key')
    def validate_device_key(self, key: str, device_key: str) -> str:
        """Validate device key format"""
        if not device_key or len(device_key) < 3:
            raise ValueError("Device key must be at least 3 characters long")
        return device_key
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if device is currently active"""
        return (
            self.status == DeviceStatus.ON and
            datetime.now(timezone.utc) - self.last_seen <= self.INACTIVITY_THRESHOLD
        )
    
    def add_metric(self, 
                   value: float, 
                   metric_type_id: int,
                   timestamp: Optional[datetime] = None,
                   metadata: Optional[Dict] = None) -> Metric:
        """
        Add a new metric and update device status
        
        Args:
            value: Metric value
            metric_type_id: Type of metric being recorded
            timestamp: Time of measurement (defaults to current time)
            metadata: Additional metric metadata
        
        Returns:
            Created metric instance
        """
        timestamp = timestamp or datetime.now(timezone.utc)
        
        metric = Metric(
            device_id=self.id,
            metric_type_id=metric_type_id,
            timestamp=timestamp,
            value=value,
            metadata=metadata or {}
        )
        
        db.session.add(metric)
        self._update_status(metric)
        self.last_seen = timestamp
        db.session.commit()
        
        return metric
    
    def batch_add_metrics(self, metrics_data: List[Dict]) -> List[Metric]:
        """
        Efficiently add multiple metrics
        
        Args:
            metrics_data: List of metric data dictionaries
        
        Returns:
            List of created metrics
        """
        metrics = []
        for data in metrics_data:
            metric = Metric(
                device_id=self.id,
                metric_type_id=data['metric_type_id'],
                timestamp=data.get('timestamp', datetime.now(timezone.utc)),
                value=data['value'],
                metadata=data.get('metadata', {})
            )
            metrics.append(metric)
        
        db.session.bulk_save_objects(metrics)
        self._update_status(metrics[-1])  # Update status based on latest metric
        self.last_seen = metrics[-1].timestamp
        db.session.commit()
        
        return metrics
    
    def get_metrics(self,
                    metric_type_id: Optional[int] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: Optional[int] = None) -> query.Query:
        """
        Get device metrics with optional filtering
        
        Args:
            metric_type_id: Filter by metric type
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of results
            
        Returns:
            Query object for metrics
        """
        query = self.metrics
        
        if metric_type_id is not None:
            query = query.filter(Metric.metric_type_id == metric_type_id)
        
        if start_time is not None:
            query = query.filter(Metric.timestamp >= start_time)
        
        if end_time is not None:
            query = query.filter(Metric.timestamp <= end_time)
            
        query = query.order_by(Metric.timestamp.desc())
        
        if limit is not None:
            query = query.limit(limit)
            
        return query
    
    def get_metric_statistics(self,
                            metric_type_id: int,
                            interval: str = '1 hour',
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Get statistical aggregates for device metrics
        
        Args:
            metric_type_id: Type of metric to analyze
            interval: Time bucket interval
            start_time: Start of analysis period
            end_time: End of analysis period
            
        Returns:
            List of statistical aggregates per time bucket
        """
        return Metric.get_timerange_stats(
            device_id=self.id,
            metric_type_id=metric_type_id,
            start_time=start_time or datetime.now(timezone.utc) - timedelta(days=1),
            end_time=end_time or datetime.now(timezone.utc),
            interval=interval
        )
    
    def _update_status(self, latest_metric: Metric) -> None:
        """Update device status based on recent metrics"""
        recent_metrics = self.get_metrics(
            metric_type_id=latest_metric.metric_type_id,
            start_time=datetime.now(timezone.utc) - self.INACTIVITY_THRESHOLD
        ).all()
        
        if len(recent_metrics) > 1:
            first_value = recent_metrics[0].value
            last_value = recent_metrics[-1].value
            avg_change = abs((last_value - first_value) / first_value)
            
            if avg_change >= self.CHANGE_THRESHOLD:
                self.status = DeviceStatus.OFF
            else:
                self.status = DeviceStatus.ON
    
    @staticmethod
    def _get_default_configuration() -> Dict:
        """Get default device configuration"""
        return {
            'sampling_rate': 60,  # seconds
            'alert_thresholds': {
                'change_rate': 0.1,
                'inactivity': 1800  # seconds
            },
            'monitoring': {
                'enabled': True,
                'metrics': ['all']
            }
        }
    
    def update(self, **kwargs) -> None:
        """Update device attributes"""
        allowed_fields = {'device_key', 'metadata', 'configuration'}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(self, field, value)
        db.session.commit()
    
    def to_dict(self, include_metrics: bool = False) -> Dict:
        """
        Convert device to dictionary
        
        Args:
            include_metrics: Whether to include recent metrics
            
        Returns:
            Dictionary representation of device
        """
        device_dict = {
            'id': self.id,
            'device_key': self.device_key,
            'user_id': self.user_id,
            'status': self.status,
            'last_seen': self.last_seen.isoformat(),
            'metadata': self.metadata,
            'configuration': self.configuration,
            'is_active': self.is_active
        }
        
        if include_metrics:
            device_dict['recent_metrics'] = [
                metric.to_dict() for metric in 
                self.get_metrics(limit=10)
            ]
            
        return device_dict

# Event listeners
@event.listens_for(Device, 'before_delete')
def cleanup_device_data(mapper, connection, target):
    """Cleanup associated data before device deletion"""
    # Using raw SQL for efficient deletion of potentially large metric datasets
    connection.execute(
        text("DELETE FROM metrics WHERE device_id = :device_id"),
        {"device_id": target.id}
    )
