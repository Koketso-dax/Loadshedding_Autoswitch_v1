""" MQTT Client Module"""
import paho.mqtt.client as mqtt
from measurement_model import Measurement

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("devices/#")

    # Create continuous aggregates when the program starts up
    Measurement.create_continuous_aggregates()

def on_message(client, userdata, msg):
    device_name = msg.topic.split('/')[1]
    data = msg.payload.decode('utf-8')
    timestamp, power_measurement = data.split(',')
    measurement = Measurement(device_name=device_name, timestamp=timestamp,
                              power_measurement=float(power_measurement))
    measurement.save()

def init_mqtt_client(app):
    """ Client init for MQTT """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(app.config['MQTT_BROKER'],
                   app.config['MQTT_PORT'], 60)
    client.loop_start()
