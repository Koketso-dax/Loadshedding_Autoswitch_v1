""" MQTT Client Module"""

import paho.mqtt.client as mqtt
from models.device import Device
from models.metric import Metric


# Send a response to device after UDP handshake
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("devices/#")


# Save metric to database
def on_message(client, userdata, msg):
    device_id = int(msg.topic.split('/')[1])
    data = msg.payload.decode('utf-8')
    timestamp, value = data.split(',')
    metric = Metric(device_id=device_id, timestamp=timestamp, value=float(value))
    metric.save()


# Initialize MQTT Broker
def init_mqtt_client(app):
    """ Client init for MQTT """
    devices = Device.query.all()
    clients = []
    for device in devices:
        client = mqtt.Client()
        client.username_pw_set(device.device_key, device.user.password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], 60)
        client.loop_start()
        clients.append(client)
    app.mqtt_clients = clients
    return clients
