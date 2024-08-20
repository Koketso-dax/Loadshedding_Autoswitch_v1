import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient # switch to timescaledb
from config import Config
from models import Device


influxdb_client = InfluxDBClient(host=Config.INFLUXDB_ADDRESS, port=Config.INFLUXDB_PORT) ##########################
influxdb_client.switch_database(Config.INFLUXDB_DATABASE) ######################

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor/data/#")

def on_message(client, userdata, msg):
    device_id = msg.topic.split('/')[-1]
    device = Device.query.filter_by(id=device_id).first()
    if device:
        data = [
            {
                "measurement": "sensor_data",
                "tags": {
                    "host": "mqtt_server",
                    "topic": msg.topic
                },
                "fields": {
                    "value": float(msg.payload.decode())
                }
            }
        ]
        influxdb_client.write_points(data)

def mqtt_client_init():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
    mqtt_client.loop_start()

if __name__ == '__main__':
    mqtt_client_init()
