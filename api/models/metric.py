"""
    Python module for data hypertables
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
from sqlalchemy import text, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates, Mapped
from sqlalchemy.orm.query import Query
from sqlalchemy.ext.hybrid import hybrid_property
from models import db


T = TypeVar('T')

class AggregationType(str, Enum):
    """Supported aggregation types for time-series data"""
    AVG = 'avg'
    MIN = 'min'
    MAX = 'max'
    SUM = 'sum'
    COUNT = 'count'
    FIRST = 'first'
    LAST = 'last'


@dataclass
class TimeSeriesResult(Generic[T]):
    """Container for time-series query results"""
    timestamp: datetime
    value: T
    device_id: int
    metadata: Optional[Dict[str, Any]] = None


class MetricType(db.Model):
    """
    Metric type configuration for different kinds of measurements
    """
    __tablename__ = 'metric_types'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(50), unique=True, nullable=False)
    unit: Mapped[str] = db.Column(db.String(20))
    description: Mapped[str] = db.Column(db.Text)
    validation_rules: Mapped[Dict] = db.Column(JSONB)
    
    metrics = relationship("Metric", back_populates="metric_type")

class Metric(db.Model):
    """
    Metric Hypertable.
    ---------------------------------------
    Attributes:
        id (int): identifier
        device_id (str): Unique device  name.
        timestamp (datetime): timestamp of the metric.
        value (float): value of the metric.
    """
    __tablename__ = 'metrics'
    __table_args__ = (
        Index('idx_metrics_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_metrics_type_timestamp', 'metric_type_id', 'timestamp'),
        {
            'timescaledb_hypertable': {
                'time_column': 'timestamp',
                'chunk_time_interval': '1 day',
                'compress_after': '7 days',
                'compression_interval': '1 day'
            }
        })

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    device_id: Mapped[int] = db.Column(db.Integer,db.ForeignKey('devices.id'), nullable=False)
    metric_type_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('metric_types.id'), nullable=False)
    timestamp: Mapped[datetime] = db.Column(db.DateTime(timezone=True), nullable=False)
    value: Mapped[float] = db.Column(db.Float, nullable=False)
    metadata: Mapped[Dict] = db.Column(JSONB, default={})
    quality: Mapped[float] = db.Column(db.Float, default=1.0)

    device = relationship("Device", back_populates="metrics")
    metric_type = relationship("MetricType", back_populates="metrics")

    def save(self) -> None:
        """ Saves the metric to the database. """
        db.session.add(self)
        db.session.commit()

    @validates('value')
    def validate_value(self, key: str, value: float) -> float:
        """Validate metric value against metric type rules"""
        if self.metric_type and self.metric_type.validation_rules:
            rules = self.metric_type.validation_rules
            if 'min' in rules and value < rules['min']:
                raise ValueError(f"Value {value} below minimum {rules['min']}")
            if 'max' in rules and value > rules['max']:
                raise ValueError(f"Value {value} above maximum {rules['max']}")
        return value

    @classmethod
    def create_continuous_aggregate(cls, view_name: str, 
                                  interval: str = '1 hour',
                                  aggregation_type: AggregationType = AggregationType.AVG):
        """Create a continuous aggregate view for the metrics"""
        sql = text(f"""
            CREATE MATERIALIZED VIEW {view_name}
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket('{interval}', timestamp) AS bucket,
                device_id,
                metric_type_id,
                {aggregation_type}(value) as value,
                count(*) as sample_count
            FROM metrics
            GROUP BY bucket, device_id, metric_type_id
            WITH NO DATA;
        """)
        db.session.execute(sql)
        db.session.commit()

    @classmethod
    def get_timerange_stats(cls, 
                           device_id: int,
                           metric_type_id: int,
                           start_time: datetime,
                           end_time: datetime,
                           interval: str = '1 hour') -> List[TimeSeriesResult]:
        """Get statistical aggregates for a time range"""
        result = db.session.query(
            func.time_bucket(interval, cls.timestamp).label('bucket'),
            func.avg(cls.value).label('avg_value'),
            func.min(cls.value).label('min_value'),
            func.max(cls.value).label('max_value'),
            func.count(cls.value).label('sample_count')
        ).filter(
            cls.device_id == device_id,
            cls.metric_type_id == metric_type_id,
            cls.timestamp.between(start_time, end_time)
        ).group_by('bucket').order_by('bucket').all()

        return [
            TimeSeriesResult(
                timestamp=r.bucket,
                value={
                    'avg': float(r.avg_value),
                    'min': float(r.min_value),
                    'max': float(r.max_value),
                    'count': int(r.sample_count)
                },
                device_id=device_id
            ) for r in result
        ]

    @classmethod
    def downsample_metrics(cls,
                          retention_policy: Dict[str, Union[str, int]]) -> None:
        """Downsample old metrics based on retention policy"""
        for interval, retention in retention_policy.items():
            sql = text(f"""
                SELECT timescaledb_toolkit.downsample(
                    relation => 'metrics',
                    time_column => 'timestamp',
                    newer_than => NOW() - INTERVAL '{retention}',
                    older_than => NOW() - INTERVAL '{retention}',
                    interval => INTERVAL '{interval}'
                );
            """)
            db.session.execute(sql)
        db.session.commit()

    @hybrid_property
    def age(self) -> timedelta:
        """Calculate age of the metric"""
        return datetime.now() - self.timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'metric_type_id': self.metric_type_id,
            'timestamp': self.timestamp.isoformat(),
            'value': float(self.value),
            'metadata': self.metadata,
            'quality': float(self.quality)
        }

    @classmethod
    def batch_insert(cls, metrics: List[Dict[str, Any]]) -> None:
        """Efficiently insert multiple metrics"""
        db.session.bulk_insert_mappings(cls, metrics)
        db.session.commit()

    @classmethod
    def get_paginated_results(cls, 
                             query: Query,
                             page: int,
                             per_page: int) -> Dict[str, Union[int, float, List[Dict[str, Any]]]]:
        """Get paginated query results with metadata"""
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'metrics': [metric.to_dict() for metric in pagination.items]
        }

    @classmethod
    def cleanup_old_data(cls, older_than: datetime) -> int:
        """Remove old data while maintaining continuous aggregates"""
        result = db.session.query(cls).filter(cls.timestamp < older_than).delete()
        db.session.commit()
        return result
