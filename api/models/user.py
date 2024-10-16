"""
    Module for the User table
"""
from typing import List, NoReturn, Union
from flask_bcrypt import Bcrypt
from models.device import Device
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Mapped
from models import db

bcrypt = Bcrypt()


class User(db.Model):
    """
        Model for storing user details.
        ------------------------------------
        Attributes:
            id (int): unique identifier for the user.
            username (str): User's display name.
            password_hash (str): Hashed password for the user.
            devices (list): User's associated devices.
    """
    __tablename__ = 'users'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    username: Mapped[str] = db.Column(db.String(128), unique=True, nullable=False)
    password_hash: Mapped[str] = db.Column(db.String(128), nullable=False)
    devices: Mapped[List[Device]] = db.relationship('Device',
                                            backref='user', lazy=True)

    @property
    def password(self) -> NoReturn:
        """ Private password property. """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password: str) -> None:
        """
        Hash password before storing it.
        --------------------------------
        :params password: User's password.
        """
        hsh: str = bcrypt.generate_password_hash(password).decode('utf-8')
        self.password_hash = hsh

    def check_password(self, password: str) -> bool:
        """
        Authenticate user password agaist hash.
        ---------------------------------------
        :param password: input password.
        :return bool: true if password is correct.
        ---------------------------------------
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def register_user(username: str, password: str) -> 'User':
        """
        Register new user.
        -----------------------------------
        :param username: User's unique name
        :param password: User's password
        :return User: newly created user
        """
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return user

    def register_device(self, device_key: str,
                        password: str) -> Union[Device, None]:
        """
        Register new device.
        --------------------
        :param device_key: Device name identifier.
        :param password: User's password.
        :return Device: newly created device
        """
        if self.check_password(password):
            device = Device(device_key=device_key, user=self)
            db.session.add(device)
            db.session.commit()
            return device
        else:
            # throw error if password is incorrect
            raise ValueError('Invalid password')

    def generate_token(self, secret_key: str,
                       expiration_minutes: int = 60) -> str:
        """
        Generate access token for user.
        -------------------------------
        :params secret_key: JWT secret key.
        :params expiration_minutes: Token expiration time in minutes.
        :return token: Generated token from user id and expiration time.
        """
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(minutes=expiration_minutes)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token: str, secret_key: str) -> Union['User', None]:
        """
        Verify access token.
        --------------------
        :params token: Client token.
        :params secret_key: Server config token.
        :returns: User object if token is valid.
        :raises: InvalidTokenError if token is invalid.
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            return User.query.get(user_id)
        except jwt.exceptions.InvalidTokenError:
            return None
