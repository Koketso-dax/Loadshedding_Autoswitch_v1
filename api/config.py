import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    INFLUXDB_ADDRESS = 'localhost'
    INFLUXDB_PORT = 8086
    INFLUXDB_DATABASE = 'mqtt_data'
    MQTT_BROKER = 'localhost'
    MQTT_PORT = 1883
