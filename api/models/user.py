"""
    Module for the User table
"""
from typing import List, NoReturn
from flask_bcrypt import Bcrypt
from models.device import Device
import jwt
from datetime import datetime, timedelta
from models import db

bcrypt = Bcrypt()


class User(db.Model):
    """
        User Model for storing user details.
        ------------------------------------
        properties:
            id: int
            username: str
            password_hash: str
            devices: list[Device]
        ------------------------------------
        methods:
            check_password: bool
            register_user: User
            register_device: Device
            generate_token: str
            verify_token: User
    """
    __tablename__ = 'users'

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(128), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(128), nullable=False)
    devices: List[Device] = db.relationship('Device', backref='user', lazy=True)

    @property
    def password(self) -> NoReturn:
        """ Private password property. """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password: str) -> None:
        """
        Hash password before storing it.
        --------------------------------
        parameters:
            password: str
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Authenticate user password agaist hash.
        ---------------------------------------
        parameters:
            password: str
        returns:
            bool
        """
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @staticmethod
    def register_user(username: str, password: str) -> 'User':
        """
        Register new user.
        ------------------
        parameters:
            username: str
            password: str
        returns:
            User
        """
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return user

    def register_device(self, device_key: str, password: str) -> Device:
        """
        Register new device.
        --------------------
        parameters:
            device_key: str
            password: str
        returns:
            Device
        """
        if self.check_password(password):
            device = Device(device_key=device_key, user=self)
            db.session.add(device)
            db.session.commit()
            return device
        else:
            # throw error if password is incorrect
            raise ValueError('Invalid password')

    def generate_token(self, secret_key: str, expiration_minutes: int=60) -> str:
        """
        Generate access token for user.
        -------------------------------
        parameters:
            secret_key: str
            expiration_minutes: int
        -------------------------------
        returns:
            token: str
        """
        payload = {
            'user_id': self.id,
            'exp': datetime.uctnow() + timedelta(minutes=expiration_minutes)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token: str, secret_key: str) -> 'User':
        """
        Verify access token.
        --------------------
        parameters:
            token: str
            secret_key: str
        returns:
            User
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            return User.query.get(user_id)
        except jwt.exceptions.InvalidTokenError:
            return None
