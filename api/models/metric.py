"""
    Python module for data hypertables
"""
from models import db
from datetime import datetime as Tdatetime
from typing import Dict, List, Union
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import Mapped


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
        {
            'timescaledb_hypertable': {
                'time_column': 'timestamp',
                'chunk_time_interval': '1 hour'}
        })

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    device_id: Mapped[int] = db.Column(db.Integer,
                                       db.ForeignKey('devices.id'))
    timestamp: Mapped[Tdatetime] = db.Column(db.DateTime())
    value: Mapped[float] = db.Column(db.Float)

    def save(self) -> None:
        """ Saves the metric to the database. """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def to_dict(query: Query, page: int,
                per_page: int) -> Dict[str, Union[int, float, List[Dict[str,
                                                            Union[str, float]
                                                            ]]
                                                  ]]:
        """
        Convert query results to a dictionary with pagination.
        ------------------------------------------------------
        :param query (Query): Input Query.
        :param page (int): Page number.
        :param per_page (int): Number of items per page.
        :return (dict): Selected query by pages.
        """
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
