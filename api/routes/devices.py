from flask import Blueprint, request, jsonify
from models.user import User
from models.device import Device
from flask_jwt_extended import jwt_required, get_jwt_identity

devices = Blueprint('devices', __name__)

# Create a new device for the user using their password.
@devices.route('/devices', methods=['POST'])
@jwt_required()
def add_device():
    """
    Add a new device for the authenticated user
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            device_key:
              type: string
              description: The unique key for the new device
            password:
              type: string
              description: The password for the authenticated user
    responses:
      201:
        description: Device added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              description: A success message
            device_id:
              type: integer
              description: The ID of the new device
      400:
        description: Missing device_key or password
      404:
        description: User not found
    """

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
@jwt_required()
def get_devices():
    """
    Retrieve all devices belonging to the authenticated user
    ---
    responses:
      200:
        description: Devices retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: The ID of the device
              device_key:
                type: string
                description: The unique key for the device
      404:
        description: User not found
    """

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    devices = [device.to_dict() for device in user.devices]
    return jsonify(devices), 200

# Retrieve a device using its id.
@devices.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    """
    Retrieve a device using its ID
    ---
    parameters:
      - name: device_id
        in: path
        type: integer
        required: true
        description: The ID of the device to retrieve
    responses:
      200:
        description: Device retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: The ID of the device
            device_key:
              type: string
              description: The unique key for the device
      404:
        description: User not found or device not found or does not belong to the user
    """

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
@jwt_required
def remove_device(device_id):
    """
    Delete a device using its ID
    ---
    parameters:
      - name: device_id
        in: path
        type: integer
        required: true
        description: The ID of the device to delete
    responses:
      200:
        description: Device removed successfully
        schema:
          type: object
          properties:
            message:
              type: string
              description: A success message
      404:
        description: User not found or device not found or does not belong to the user
    """

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
