#!/usr/bin/env python3
"""
Route to handle all authentication in the backend.
"""
from __future__ import annotations
from config import Config
from typing import TypedDict, Tuple, Optional, Dict, Any
from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    unset_jwt_cookies
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.user import User, UserStatus
import re

# Type definitions
class TokenResponse(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class AuthResponse(TypedDict):
    message: str
    data: Optional[Dict[str, Any]]

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Create blueprint
auth = Blueprint('auth', __name__)

# Constants
MIN_PASSWORD_LENGTH = 8
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,32}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_registration_input(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate registration input data.
    
    Args:
        data: Registration request data
        
    Returns:
        Tuple of (error message, validated data)
    """
    required_fields = ['username', 'email', 'password']
    
    # Check required fields
    if not all(field in data for field in required_fields):
        return 'Missing required fields', None
        
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    
    # Validate username
    if not USERNAME_PATTERN.match(username):
        return 'Invalid username format. Use 3-32 alphanumeric characters, underscores, or hyphens.', None
        
    # Validate email
    if not EMAIL_PATTERN.match(email):
        return 'Invalid email format', None
        
    # Validate password
    if not PASSWORD_PATTERN.match(password):
        return 'Password must be at least 8 characters and contain letters and numbers', None
        
    return None, {
        'username': username,
        'email': email,
        'password': password,
        'metadata': data.get('metadata', {})
    }

@auth.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register() -> Tuple[Response, int]:
    """
    Register a new user with validation.
    
    Returns:
        Response with 201 on success, error code otherwise
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        error, validated_data = validate_registration_input(data)
        if error:
            return jsonify({'message': error}), 400
            
        # Check existing username
        if User.query.filter_by(username=validated_data['username']).first():
            return jsonify({'message': 'Username already exists'}), 409
            
        # Check existing email
        if User.query.filter_by(email=validated_data['email']).first():
            return jsonify({'message': 'Email already registered'}), 409
            
        # Create user
        user = User.register_user(**validated_data)
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        response: AuthResponse = {
            'message': 'User registered successfully',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': int(Config.JWT_ACCESS_TOKEN_EXPIRES)
            }
        }
        
        return jsonify(response), 201
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login() -> Tuple[Response, int]:
    """
    Authenticate user and issue JWT tokens.
    
    Returns:
        Response with 200 and tokens on success, error code otherwise
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        identifier = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))
        
        if not identifier or not password:
            return jsonify({'message': 'Missing login credentials'}), 400
            
        # Find user by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
            
        # Check user status
        if user.status != UserStatus.ACTIVE:
            return jsonify({'message': f'Account is {user.status}'}), 403
            
        # Verify password
        try:
            if not user.check_password(password):
                return jsonify({'message': 'Invalid credentials'}), 401
        except ValueError as e:
            return jsonify({'message': str(e)}), 429
            
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        response: TokenResponse = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': int(Config.JWT_ACCESS_TOKEN_EXPIRES)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh() -> Tuple[Response, int]:
    """
    Refresh access token using refresh token.
    
    Returns:
        Response with 200 and new access token, error code otherwise
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.status != UserStatus.ACTIVE:
            return jsonify({'message': 'Invalid token'}), 401
            
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': int(Config.JWT_ACCESS_TOKEN_EXPIRES)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout() -> Tuple[Response, int]:
    """
    Logout user and invalidate tokens.
    
    Returns:
        Response with 200 on success
    """
    try:
        jti = get_jwt()['jti']
        unset_jwt_cookies(jsonify({'message': 'Successfully logged out'}))
        return jsonify({'message': 'Successfully logged out'}), 200

    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile() -> Tuple[Response, int]:
    """
    Get current user's profile.
    
    Returns:
        Response with 200 and user data on success
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify({
            'message': 'Success',
            'data': user.to_dict(include_devices=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Profile retrieval error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Error handlers
@auth.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({'message': 'Rate limit exceeded'}), 429

@auth.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    current_app.logger.error(f"Internal server error: {str(e)}")
    return jsonify({'message': 'Internal server error'}), 500
