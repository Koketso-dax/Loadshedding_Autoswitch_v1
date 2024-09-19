"""
    Python module for data hypertables
"""
from models import db
from sqlalchemy import Pagination

class Measurement(db.Model):
    """ Class definition for measurement Hypertable """
    __tablename__ = 'measurements'
    __table_args__ = (
        {
            'timescaledb_hypertable': {
                'time_column': 'timestamp',
                'chunk_time_interval': '1 hour'}
        }
        )

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    timestamp = db.Column(db.DateTime())
    power_measurement = db.Column(db.Float)

    device = db.relationship('Device')

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def to_dict(query, page, per_page):
        """ Convert query results to a dictionary with pagination """
        pagination = query.paginate(page, per_page, error_out=False)
        measurements = pagination.items
        return {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'measurements': [
                {
                    'timestamp': measurement.timestamp.isoformat(),
                    'power_measurement': measurement.power_measurement
                }
                for measurement in measurements
            ]
        }
