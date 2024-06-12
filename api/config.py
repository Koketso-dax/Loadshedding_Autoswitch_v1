import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://dev:password@localhost/loadshedding'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_key')
    INFLUXDB_ADDRESS = 'web-01.koketsodiale.tech'
    INFLUXDB_PORT = 8086
    INFLUXDB_DATABASE = 'loadshedding'
    MQTT_BROKER = 'web-01.koketsodiale.tech'
    MQTT_PORT = 1883
