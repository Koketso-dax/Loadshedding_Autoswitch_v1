""" MQTT Client Module"""
import paho.mqtt.client as mqtt
from models.device import Device
from models.measurement import Measurement
from models import db

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("devices/#")

def on_message(client, userdata, msg):
    device_id = int(msg.topic.split('/')[1])
    data = msg.payload.decode('utf-8')
    timestamp, power_measurement = data.split(',')
    measurement = Measurement(device_id=device_id, timestamp=timestamp, power_measurement=float(power_measurement))
    measurement.save()

def init_mqtt_client(app):
    """ Client init for MQTT """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], 60)
    client.loop_start()
