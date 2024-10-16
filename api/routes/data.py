"""
Data manipulation routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.device import Device
from models.metric import Metric
from typing import Dict, Union, Tuple


data = Blueprint('data', __name__)


@data.route('/data/<device_id>', methods=['GET'])
@jwt_required()
def get_device_data(device_id: int) -> Union[Dict[str,
                                             Union[int, str, float]],
                                             Tuple[Dict[str, str], int]]:
    """
    Get data for a specific device by id.
    -------------------------------------
    :param device_id: The ID of the device to retrieve data for.
    :return: A JSON response containing the device data.
    """
    user_id: str = get_jwt_identity()
    device: Device = Device.query.get(device_id)

    # Check if device exists and belongs to the user.
    if not device or device.user_id != user_id:
        return jsonify({'message': 'Device not found'}), 404

    # Retrieve metrics for the device.
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = Metric.query.filter_by(device_id=device_id).order_by(
        Metric.timestamp.desc())
    data = Metric.to_dict(query, page, per_page)
    return jsonify(data), 200
