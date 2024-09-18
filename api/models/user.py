"""
    Module for the User table
"""
from flask_bcrypt import Bcrypt
from models.device import Device
import jwt
from datetime import datetime, timedelta
from models import db

bcrypt = Bcrypt()


class User(db.Model):
    """ User table class """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    devices = db.relationship('Device', backref='user', lazy=True)

    @property
    def password(self):
        # ensure password is unreadable
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        # hash password before storing it
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        # authenticate password
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @staticmethod
    def register_user(username, password):
        # create new user
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return user

    def register_device(self, device_key, password):
        # create new device for user
        if self.check_password(password):
            device = Device(device_key=device_key, user=self)
            db.session.add(device)
            db.session.commit()
            return device
        else:
            # throw error if password is incorrect
            raise ValueError('Invalid password')

    def generate_token(self, secret_key, expiration_minutes=60):
        # generate access token for user on login
        payload = {
            'user_id': self.id,
            'exp': datetime.uctnow() + timedelta(minutes=expiration_minutes)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token, secret_key):
        # check token on request
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            return User.query.get(user_id)
        except jwt.exceptions.InvalidTokenError:
            return None
