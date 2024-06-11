from flask import Blueprint, request, jsonify
from influxdb import InfluxDBClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Device, db

data = Blueprint('data', __name__)

influxdb_client = InfluxDBClient(host=Config.INFLUXDB_ADDRESS, port=Config.INFLUXDB_PORT)
influxdb_client.switch_database(Config.INFLUXDB_DATABASE)

@data.route('/data/<device_id>', methods=['GET'])
@jwt_required()
def get_device_data(device_id):
    user_id = get_jwt_identity()
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        return jsonify({'message': 'Device not found'}), 404

    query = f'SELECT * FROM sensor_data WHERE "topic" = \'sensor/data/{device_id}\''
    result = influxdb_client.query(query)
    data_points = list(result.get_points())

    return jsonify(data_points)
