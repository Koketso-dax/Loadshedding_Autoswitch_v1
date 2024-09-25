import os
from dotenv import load_dotenv


load_dotenv()
# Define class for config.
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MQTT_BROKER = '127.0.0.1'
    MQTT_PORT = 1883
