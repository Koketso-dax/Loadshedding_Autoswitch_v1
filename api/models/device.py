"""
    Python module for Device Table
"""
from flask_sqlalchemy import SQLAlchemy
from models import db
from models.measurement import Measurement


class Device(db.Model):
    """
        Class for Device Table
    """
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    device_key = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='devices')
    measurements = db.relationship('Measurement', backref='devices')

    def __init__(self, device_key, user):
        self.device_key = device_key
        self.user = user

    def get_measurements(self):
        return self.measurements

    def add_measurements(self, timestamp, power_measurement):
        measurements = Measurement(timestamp=timestamp,
                                   power_measurement=power_measurement,
                                   device = self)
        db.session.add(measurements)
        db.session.commit()

    def delete(self):
        for measurement in self.measurements:
            db.session.delete(measurement)
        db.session.delete(self)
        db.session.commit()

    def update_device_key(self, new_device_key):
        self.device_key = new_device_key
        db.session.commit()
