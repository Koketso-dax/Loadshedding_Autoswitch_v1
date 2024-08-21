from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.device import Device
from models.measurement import Measurement

data = Blueprint('data', __name__)

@data.route('/data/<device_id>', methods=['GET'])
@jwt_required()
def get_device_data(device_id):
    user_id = get_jwt_identity()
    device = Device.query.get(device_id)

    if not device or device.user_id != user_id:
        return jsonify({'message': 'Device not found'}), 404

    measurements = Measurement.query.filter_by(device_id=device_id).all()
    data = [measurement.to_dict() for measurement in measurements]
    return jsonify(data), 200
