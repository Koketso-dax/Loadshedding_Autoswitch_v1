from flask import Blueprint, request, jsonify
from models.user import User
from models.device import Device
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger.utils import swag_from

devices = Blueprint('devices', __name__)

# Create a new device for the user using their password.
@devices.route('/devices', methods=['POST'])
@swag_from('/docs/devices.yml', methods=['POST'])
@jwt_required()
def add_device():
    device_key = request.json.get('device_key')
    password = request.json.get('password')

    # Validate the input
    if not device_key or not password:
        return jsonify({'message': 'Missing device_key or password'}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check if the user exists
    if not user:
        return jsonify({'message': 'User not found'}), 404

    device = user.register_device(device_key, password)
    return jsonify({'message': 'Device added successfully', 'device_id': device.id}), 201

# Retrieve all devices belonging to a user.
@devices.route('/devices', methods=['GET'])
@swag_from('/docs/devices.yml', methods=['GET'])
@jwt_required()
def get_devices():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    devices = [device.to_dict() for device in user.devices]
    return jsonify(devices), 200

# Retrieve a device using its id.
@devices.route('/<int:device_id>', methods=['GET'])
@swag_from('/docs/devices.yml/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    device = Device.query.get(device_id)

    if not device or device.user_id != user.id:
        return jsonify({'message': 'Device not found'}), 404

    return jsonify(device.to_dict()), 200

# delete a device
@devices.route('/<int:device_id>', methods=['DELETE'])
@swag_from('/docs/devices.yml/<int:device_id>', methods=['DELETE'])
@jwt_required
def remove_device(device_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Check if user exists
    if not user:
        return jsonify({'message': 'User not found'}), 404

    device = Device.query.get(device_id)

    # Check if device exists and belongs to the user
    if not device or device.user_id != user.id:
        return jsonify({'message': 'Device not found'}), 404

    # delete device
    device.delete()
    return jsonify({'message': 'Device removed successfully'}), 200
