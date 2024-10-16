from flask import Blueprint, request, jsonify
from models.user import User
from models.device import Device
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Union, List, Tuple

devices = Blueprint('devices', __name__)


@devices.route('/devices', methods=['POST'])
@jwt_required()
def add_device() -> Union[Dict[str, Union[str, int]],
                          Tuple[Dict[str, str], int]]:
    """
    Add a new device to the user's account.
    ---------------------------------------
    :return: A JSON response containing the device ID.
    """
    device_key: str = request.json.get('device_key')
    password: str = request.json.get('password')

    # Validate the input
    if not device_key or not password:
        return jsonify({'message': 'Missing device_key or password'}), 400

    user_id: int = get_jwt_identity()
    user: User = User.query.get(user_id)

    # Check if the user exists
    if not user:
        return jsonify({'message': 'User not found'}), 404

    device: Device = user.register_device(device_key, password)
    return jsonify({'message': 'Device added successfully',
                    'device_id': device.id}), 201


@devices.route('/devices', methods=['GET'])
@jwt_required()
def get_devices() -> Union[List[Dict[str, Union[int, str]]],
                           Tuple[Dict[str, str], int]]:
    """
    Get all devices associated with the user's account.
    --------------------------------------------------
    :return: A JSON response containing a list of devices.
    """
    user_id: int = get_jwt_identity()
    user: User = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    devices: List[Dict[str, Union[int, str]]] = [device.to_dict()
                                                 for device in user.devices]
    return jsonify(devices), 200


@devices.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id) -> Union[Dict[str, Union[int, str]],
                                   Tuple[Dict[str, str], int]]:
    """
    Get a specific device by ID.
    ----------------------------
    :param device_id: The ID of the device to retrieve.
    :return: A JSON response containing the device data.
    """
    user_id: int = get_jwt_identity()
    user: User = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    device = Device.query.get(device_id)

    if not device or device.user_id != user.id:
        return jsonify({'message': 'Device not found'}), 404

    return jsonify(device.to_dict()), 200


@devices.route('/<int:device_id>', methods=['DELETE'])
@jwt_required
def remove_device(device_id) -> Union[Dict[str, str],
                                      Tuple[Dict[str, str], int]]:
    """
    Remove a device from the user's account.
    ----------------------------------------
    :param device_id: The ID of the device to remove.
    :return: A JSON response indicating success or failure.
    """
    user_id: int = get_jwt_identity()
    user: User = User.query.get(user_id)

    # Check if user exists
    if not user:
        return jsonify({'message': 'User not found'}), 404

    device: Device = Device.query.get(device_id)

    # Check if device exists and belongs to the user
    if not device or device.user_id != user.id:
        return jsonify({'message': 'Device not found'}), 404

    # delete device
    device.delete()
    return jsonify({'message': 'Device removed successfully'}), 200
