from flask import Blueprint, request, jsonify
from models.user import User
from models.device import Device
from flask_jwt_extended import jwt_required, get_jwt_identity

devices = Blueprint('devices', __name__)

@devices.route('/devices', methods=['POST'])
@jwt_required()
def add_device():
    device_key = request.json.get('device_key')
    password = request.json.get('password')

    if not device_key or not password:
        return jsonify({'message': 'Missing device_key or password'}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    device = user.register_device(device_key, password)
    return jsonify({'message': 'Device added successfully', 'device_id': device.id}), 201

@devices.route('/devices', methods=['GET'])
@jwt_required()
def get_devices():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    devices = [device.to_dict() for device in user.devices]
    return jsonify(devices), 200

@devices.route('/<int:device_id>', methods=['DELETE'])
@jwt_required
def remove_device(device_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    device = Device.query.get(device_id)

    if not device or device.user_id != user.id:
        return jsonify({'message': 'Device not found'}), 404

    device.delete()
    return jsonify({'message': 'Device removed successfully'}), 200
