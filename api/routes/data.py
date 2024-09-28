"""
Data manipulation routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.device import Device
from models.metric import Metric
data = Blueprint('data', __name__)

# Retrieve device data by id.
@data.route('/data/<device_id>', methods=['GET'])
@jwt_required()
def get_device_data(device_id):
    """
    Retrieve metrics for a device
    ---
    parameters:
      - name: device_id
        in: path
        type: integer
        required: true
        description: The ID of the device to retrieve metrics for
      - name: page
        in: query
        type: integer
        default: 1
        description: The page number to retrieve (default is 1)
      - name: per_page
        in: query
        type: integer
        default: 10
        description: The number of metrics to retrieve per page (default is 10)
    responses:
      200:
        description: Metrics retrieved successfully
        schema:
          type: object
          properties:
            page:
              type: integer
              description: The current page number
            per_page:
              type: integer
              description: The number of metrics per page
            total_pages:
              type: integer
              description: The total number of pages
            total_items:
              type: integer
              description: The total number of metrics
            metrics:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                    format: date-time
                    description: The timestamp of the metric
                  value:
                    type: number
                    description: The value of the metric
      401:
        description: Missing or invalid JWT token
      404:
        description: Device not found or does not belong to the user
    """

    user_id = get_jwt_identity()
    device = Device.query.get(device_id)

    # Check if device exists and belongs to the user.
    if not device or device.user_id != user_id:
        return jsonify({'message': 'Device not found'}), 404

    # Retrieve metrics for the device.
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = Metric.query.filter_by(device_id=device_id).order_by(Metric.timestamp.desc())
    data = Metric.to_dict(query, page, per_page)
    return jsonify(data), 200
