"""
Route to handle all authentication in the backend.
"""
from flask import Blueprint, request, jsonify
from models.user import User
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

# Create route to handle registration from client side.
@auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: The username for the new user
            password:
              type: string
              description: The password for the new user
    responses:
      201:
        description: User created successfully
      400:
        description: Missing username or password, or username already exists
    """
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if username or password is missing
    if not username or not password:
        return jsonify({'message' : 'Missing username or password'}), 400

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message' : 'Username already exists'}), 400

    User.register_user(username, password)
    return jsonify({'message' : 'User created succesfully'}), 201

# Create route to handle login functionality using jwt.
@auth.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return an access token
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: The username of the user to authenticate
            password:
              type: string
              description: The password of the user to authenticate
    responses:
      200:
        description: Authentication successful
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: The access token for the authenticated user
      400:
        description: Missing username or password
      401:
        description: Invalid username or password
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
