"""
    Python module for data hypertables
"""
from models import db


class Metric(db.Model):
    """
    Class definition for metric Hypertable
    ---
    Attributes:
        id: primary key
        device_id: foreign key to devices table
        timestamp: timestamp of the metric
        value: value of the metric
    ---
    Methods:
        save: save a metric to the database
        to_dict: convert query results to a dictionary with pagination
    ---
    Hypertable:
        timescaledb_hypertable: creates a hypertable from the table
        chunk_time_interval: sets the chunk time interval to 1 hour
        time_column: sets the time column to timestamp
    """
    __tablename__ = 'metrics'
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
    value = db.Column(db.Float)

    device = db.relationship('Device')

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def to_dict(query, page, per_page):
        """ Convert query results to a dictionary with pagination """
        pagination = query.paginate(page, per_page, error_out=False)
        metrics = pagination.items
        return {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'metrics': [
                {
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.value
                }
                for metric in metrics
            ]
        }
