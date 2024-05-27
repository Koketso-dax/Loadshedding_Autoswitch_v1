import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
    INFLUXDB_PORT = int(os.getenv('INFLUXDB_PORT', 8086))
    INFLUXDB_DATABASE = os.getenv('INFLUXDB_DATABASE', 'mydb')
