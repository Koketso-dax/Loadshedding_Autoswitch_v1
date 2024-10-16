"""
Route to handle all authentication in the backend.
"""
from flask import Blueprint, request, jsonify
from models.user import User
from flask_jwt_extended import create_access_token
from flask import Response
from typing import Literal, Union, Tuple

auth = Blueprint('auth', __name__)


# Registration (Create User)
@auth.route('/register', methods=['POST'])
def register() -> (Tuple[Response,
                         Literal[400]] | Tuple[Response,
                                               Literal[201]]):
    """
    Register a new user.
    --------------------
    :param username: User's unique name
    :param password: User's password
    :return User: newly created user
    """
    username: str = request.json.get('username')
    password: str = request.json.get('password')

    # Check if username or password is missing
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    User.register_user(username, password)
    return jsonify({'message': 'User created succesfully'}), 201


# Login (JWT Authentication)
@auth.route('/login', methods=['POST'])
def login() -> Union[Tuple[Response, Literal[400]],
                     Tuple[Response, Literal[401]],
                     Tuple[Response, Literal[200]]]:
    """
    Login a user (JWT token creation).
    --------------------
    :param username: User's unique name
    :param password: User's password
    :return User: newly created user
    """
    username = request.json.get('username')
    password = request.json.get('password')

    # return 400 if username or password is missing
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()

    # return 401 if password is incorrect
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    # create access_token for user with user.id
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200
