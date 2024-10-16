"""
    Python module for Device Table
"""
from models import db
from models.metric import Metric
from models.user import User
from datetime import timedelta, datetime
from typing import List, Dict, Union
from sqlalchemy.orm import Mapped


class Device(db.Model):
    """
        Class representation of Devices.
        --------------------------------
        Attributes:
            id (int): Device identifier.
            device_key (str): Device name.
            user_id (int): User identifier to device.
            state (bool): Device state (on/off)
            metrics (list): Device recorded metrics.
    """
    __tablename__ = 'devices'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    device_key: Mapped[str] = db.Column(db.String(128), nullable=False)
    user_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('users.id'),
                             nullable=False)
    state: Mapped[str] = db.Column(db.String(10), default='on')

    metrics: Mapped[List[Metric]] = db.relationship('Metric')

    def __init__(self, device_key: str, user: User):
        self.device_key = device_key
        self.user = user

    def get_metrics(self) -> List[Metric]:
        """
        Retrieves metrics for current device.
        ---------------------------------------------
        :return: list of metrics for current device
        """
        return self.metrics

    def add_metric(self, timestamp: datetime, value: float) -> None:
        """
        Adds a new metric and updates state.
        -----------------------------------------------
        :params timestamp: Time of capture.
        :params value: Value of energy reading. """
        metric = Metric(timestamp=timestamp,
                        value=value,
                        device=self)
        db.session.add(metric)
        db.session.commit()

        # calculate average value change over the past 30 minutes
        thirty_minutes_ago = datetime.now(datetime.timezone.utc) \
            - timedelta(minutes=30)
        recent_metrics = Metric.query.filter(
            Metric.device_id == self.id,
            Metric.timestamp >= thirty_minutes_ago
        ).all()
        if len(recent_metrics) > 1:
            first_value = recent_metrics[0].value
            last_value = recent_metrics[-1].value
            avg_change = abs((last_value - first_value) / first_value)
            if avg_change >= 0.1:
                self.state = 'off'
                db.session.commit()

    def delete(self) -> None:
        """ Deletes a device and its associated metrics. """
        for metric in self.metrics:
            db.session.delete(metric)
        db.session.delete(self)
        db.session.commit()

    def update_device_key(self, new_device_key: str) -> None:
        """
        Updates the device key for the device.
        --------------------------------------
        :param new_device_key: New device name.
        """
        self.device_name = new_device_key
        db.session.commit()

    def to_dict(self) -> Dict[str, Union[int, str]]:
        """
        Converts device object to dictionary.
        --------------------------------------
        :returns dict: dictionary representation of device
        """
        return {
            'id': self.id,
            'device_key': self.device_key,
            'state': self.state,
        }
