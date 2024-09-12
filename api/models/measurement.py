"""
    Python module for data hypertables
"""
from models import db


class Measurement(db.Model):
    """ Class definition for measurement Hypertable """
    __tablename__ = 'measurements'
    __table_args__ = {'__timescaledb_hypertable__': {'time_column': 'timestamp', 'chunk_time_interval': '1 day'}}

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    timestamp = db.Column(db.DateTime())
    power_measurement = db.Column(db.Float)

    device = db.relationship('Device', backref='device_measurements')

    def save(self):
        db.session.add(self)
        db.session.commit()