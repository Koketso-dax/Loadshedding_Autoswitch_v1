from flask_sqlalchemy import SQLAlchemy
from api.models.base_model import Base

db = SQLAlchemy(model_class=Base)


class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    device_key = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='devices')
    measurements = db.relationship('Measurement', back_populates='device')
