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
        Class for Device Table
    """
    __tablename__ = 'devices'

    # Data members for devices
    id = db.Column(db.Integer, primary_key=True)
    device_key = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    state = db.Column(db.String(10), default='on')
    #relationship with metrics table
    metrics = db.relationship('Metric')

    def __init__(self, device_key, user):
        self.device_key = device_key
        self.user = user

    def get_metrics(self):
        # retrieve metrics for specific device
        return self.metrics

    def add_metric(self, timestamp, value):  # update method name to add_metric
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
        # remove a device
        for metric in self.metrics:  # update loop variable to metric
            db.session.delete(metric)
        db.session.delete(self)
        db.session.commit()

    def update_device_key(self, new_device_key):
        # Update a device's name
        self.device_name = new_device_key
        db.session.commit()

    def to_dict(self):
        # device properties
        return {
            'id': self.id,
            'device_key': self.device_key,
            'state': self.state,
        }
