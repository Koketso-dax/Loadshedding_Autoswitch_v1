"""
    Module for the User table
"""
from __future__ import annotations
from enum import Enum
from typing import List, NoReturn, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from flask_bcrypt import Bcrypt
from sqlalchemy import event, Index, text
from sqlalchemy.orm import mapped_column, relationship, validates, Mapped
from sqlalchemy.dialects.postgresql import JSONB
import jwt
from models import db
from models.device import Device


bcrypt = Bcrypt()


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING_VERIFICATION = 'pending_verification'


class User(db.Model):
    """
    Model for user management and authentication.

    Attributes:
        id: Unique identifier
        username: Unique username
        email: User's email address
        password_hash: Securely hashed password
        status: Current account status
        metadata: Additional user information
        devices: Associated devices
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last successful login
    """
    __tablename__ = 'users'

    # Primary columns
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(128),
                                          unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(255),
                                       unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        db.Enum(UserStatus),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False
    )
    metadata: Mapped[Dict] = mapped_column(JSONB, default={}, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        db.DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    devices: Mapped[List[Device]] = relationship(
        'Device',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # Indexes
    __table_args__ = (
        Index('idx_user_username_email', 'username', 'email'),
        Index('idx_user_status', 'status'),
        Index('idx_user_metadata_gin', metadata, postgresql_using='gin')
    )

    # Configuration constants
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 128
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_TIMEOUT = timedelta(minutes=15)
    TOKEN_EXPIRATION = timedelta(hours=1)
    DEVICE_LIMIT = 10

    def __init__(self, username: str, email: str, password: str,
                 metadata: Optional[Dict] = None) -> None:
        """
        Initialize a new user instance.

        Args:
            username: Unique username
            email: Valid email address
            password: Secure password
            metadata: Optional user metadata

        Raises:
            ValueError: If any validation fails
        """
        self.username = username
        self.email = email
        self.password = password  # Will be hashed via property
        self.metadata = metadata or {}
        self._failed_login_attempts = 0
        self._last_login_attempt = None

    @validates('username')
    def validate_username(self, key: str, username: str) -> str:
        """Validate username format"""
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        if not (self.USERNAME_MIN_LENGTH
                <= len(username) <= self.USERNAME_MAX_LENGTH):
            raise ValueError(
                f"Username must be between {self.USERNAME_MIN_LENGTH} and "
                f"{self.USERNAME_MAX_LENGTH} characters"
            )

        if not username.isalnum():
            raise ValueError("Username must be alphanumeric")

        return username

    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        """Validate email format"""
        import re
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")

        return email.lower()

    @property
    def password(self) -> NoReturn:
        """Prevent password access"""
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password: str) -> None:
        """Hash and set password"""
        if not password or len(password) < self.PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"Password must be at least \
                {self.PASSWORD_MIN_LENGTH} characters"
            )
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify password and handle login attempts.

        Args:
            password: Password to verify

        Returns:
            bool: True if password matches

        Raises:
            ValueError: If account is locked
        """
        now = datetime.now(timezone.utc)

        # Check if account is locked
        if (self._failed_login_attempts >= self.MAX_LOGIN_ATTEMPTS and
            self._last_login_attempt and
                now - self._last_login_attempt < self.LOGIN_TIMEOUT):
            raise ValueError(
                f"Account is locked. Try again in "
                f"{(self.LOGIN_TIMEOUT - (now - self._last_login_attempt)).seconds // 60} minutes"
            )

        # Verify password
        is_valid = bcrypt.check_password_hash(self.password_hash, password)

        if is_valid:
            self._failed_login_attempts = 0
            self.last_login = now
        else:
            self._failed_login_attempts += 1
            self._last_login_attempt = now

        return is_valid

    def generate_token(self, secret_key: str,
                       expiration: Optional[timedelta] = None) -> str:
        """
        Generate JWT access token.

        Args:
            secret_key: JWT secret key
            expiration: Optional custom expiration time

        Returns:
            str: Encoded JWT token
        """
        expiration = expiration or self.TOKEN_EXPIRATION
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.now(timezone.utc) + expiration
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def verify_token(token: str, secret_key: str) -> Optional[User]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify
            secret_key: Server secret key

        Returns:
            Optional[User]: User instance if token is valid
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user = User.query.get(payload['user_id'])

            if user and user.username == payload['username']:
                return user
            return None

        except jwt.InvalidTokenError:
            return None

    @classmethod
    def register_user(cls, username: str, email: str,
                      password: str, metadata: Optional[Dict] = None) -> User:
        """
        Register new user with validation.

        Args:
            username: Unique username
            email: Valid email address
            password: Secure password
            metadata: Optional user metadata

        Returns:
            User: New user instance

        Raises:
            ValueError: If registration fails
        """
        try:
            user = cls(
                username=username,
                email=email,
                password=password,
                metadata=metadata
            )
            db.session.add(user)
            db.session.commit()
            return user

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to register user: {str(e)}")

    def register_device(self, device_key: str,
                        password: str,
                        metadata: Optional[Dict] = None) -> Device:
        """
        Register new device with validation.

        Args:
            device_key: Unique device identifier
            password: User password for verification
            metadata: Optional device metadata

        Returns:
            Device: New device instance

        Raises:
            ValueError: If registration fails or limit reached
        """
        if not self.check_password(password):
            raise ValueError("Invalid password")

        if self.devices.count() >= self.DEVICE_LIMIT:
            raise ValueError(f"Device limit of {self.DEVICE_LIMIT} reached")

        try:
            device = Device(
                device_key=device_key,
                user=self,
                metadata=metadata
            )
            db.session.add(device)
            db.session.commit()
            return device

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to register device: {str(e)}")

    def get_active_devices(self) -> List[Device]:
        """Get list of currently active devices"""
        return self.devices.filter(
            Device.status == Device.DeviceStatus.ACTIVE
        ).all()

    def to_dict(self, include_devices: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.

        Args:
            include_devices: Whether to include device information

        Returns:
            Dict: User data dictionary
        """
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'status': self.status,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat()
            if self.last_login else None
        }

        if include_devices:
            user_dict['devices'] = [
                device.to_dict() for device in self.devices.all()
            ]

        return user_dict


# Event listeners
@event.listens_for(User, 'before_delete')
def cleanup_user_data(mapper, connection, target):
    """Cleanup associated data before user deletion"""
    connection.execute(
        text("DELETE FROM devices WHERE user_id = :user_id"),
        {"user_id": target.id}
    )
