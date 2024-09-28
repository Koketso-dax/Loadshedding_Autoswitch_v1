"""
    Python module for Device Table
"""
from models import db
from models.metric import Metric
import datetime
from datetime import timedelta

# Define Devices Table

class Device(db.Model):
    """
        Class representation of Devices
        ---
        properties:

            id: int
            device_key: str
            user_id: int
            state: str
            metrics: list

        methods:

            get_metrics: list
            add_metric: None
            delete: None
            update_device_key: None
            to_dict: dict
    """
    __tablename__ = 'devices'

    # Data members for devices
    id = db.Column(db.Integer, primary_key=True)
    device_key = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'), nullable=False)
    state = db.Column(db.String(10), default='on')
    #relationship with metrics table
    metrics = db.relationship('Metric')

    def __init__(self, device_key, user):
        self.device_key = device_key
        self.user = user

    def get_metrics(self):
        """
        Retrieves metrics for current device.
        ---

        Returns:
            list: list of metrics for current device

        """
        return self.metrics

    def add_metric(self, timestamp, value):
        """
        Adds a new metric to the device & checks if the device should be
        turned off based on the average value change over the past 30 min.
        ---

        Parameters:
            timestamp: datetime
            value: int
        """
        metric = Metric(timestamp=timestamp,
                        value=value,
                        device=self)
        db.session.add(metric)
        db.session.commit()

        # calculate average value change over the past 30 minutes
        thirty_minutes_ago = datetime.now(datetime.timezone.utc) - timedelta(minutes=30)
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

    def delete(self):
        """
        Deletes a device and its associated metrics.
        ---

        """
        for metric in self.metrics:
            db.session.delete(metric)
        db.session.delete(self)
        db.session.commit()

    def update_device_key(self, new_device_key):
        """
        Updates the device key for the current device.
        ---

        Parameters:

            new_device_key: str

        """
        self.device_name = new_device_key
        db.session.commit()

    def to_dict(self):
        """
        Converts device object to dictionary.
        ---
        """
        return {
            'id': self.id,
            'device_key': self.device_key,
            'state': self.state,
        }
