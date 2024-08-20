from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    devices = db.relationship('Device', backpopulates='user')

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_key = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='devices')

