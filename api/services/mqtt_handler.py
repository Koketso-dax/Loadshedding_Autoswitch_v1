""" MQTT Client Module"""
import paho.mqtt.client as mqtt
from models.device import Device
from models.measurement import Measurement
from models import db


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("devices/#")

def on_message(client, userdata, msg):
    device_key = msg.topic.split('/')[1]
    device = Device.query.filter_by(device_key=device_key).first()

    if not device:
        print(f"Device with key {device_key} not found")
        return

    data = msg.payload.decode('utf-8')
    timestamp, power_measurement = data.split(',')
    measurement = Measurement(device=device, timestamp=timestamp, power_measurement=float(power_measurement))
    db.session.add(measurement)
    db.session.commit()

def init_mqtt_client(app):
    """ Client init for MQTT """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(app.config['MQTT_BROKER'],
                   app.config['MQTT_PORT'], 60)
    client.loop_start()
