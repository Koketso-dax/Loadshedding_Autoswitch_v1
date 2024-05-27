from influxdb import InfluxDBClient
from config import Config

client = InfluxDBClient(host=Config.INFLUXDB_HOST, port=Config.INFLUXDB_PORT)
client.switch_database(Config.INFLUXDB_DATABASE)

from models.user import User
from models.device import Device
