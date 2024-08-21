from flask import Blueprint, request, jsonify
from models.user import User
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message' : 'Missing username or password'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message' : 'Username already exists'}), 400

    user = User.register_user(username, password)
    return jsonify({'message' : 'User created succesfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200
