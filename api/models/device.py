"""
    Python module for Device Table
"""
from models import db
from models.metric import Metric

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
    #relationship with metrics table
    metrics = db.relationship('Metric')  # update relationship to Metric

    def __init__(self, device_key, user):
        self.device_key = device_key
        self.user = user

    def get_metrics(self):  # update method name to get_metrics
        # retrieve metrics for specific device
        return self.metrics

    def add_metric(self, timestamp, value):  # update method name to add_metric
        metric = Metric(timestamp=timestamp,
                        value=value,
                        device=self)
        db.session.add(metric)
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
        }