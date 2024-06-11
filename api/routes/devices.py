from flask import Blueprint, request, jsonify
from models import Device, db
from flask_jwt_extended import jwt_required, get_jwt_identity

devices = Blueprint('devices', __name__)

@devices.route('/devices', methods=['POST'])
@jwt_required()
def add_device():
    data = request.get_json()
    user_id = get_jwt_identity()
    device = Device(name=data['name'], user_id=user_id)
    db.session.add(device)
    db.session.commit()
    return jsonify({'message': 'Device registered successfully'})

@devices.route('/devices', methods=['GET'])
@jwt_required()
def get_devices():
    user_id = get_jwt_identity()
    devices = Device.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': d.id, 'name': d.name} for d in devices])
