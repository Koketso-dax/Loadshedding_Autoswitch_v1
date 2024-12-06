"""
Main program for the Flask API.
Author: Koketso Diale
Date: 2024-07-22
"""
from __future__ import annotations
from routes.auth import auth
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from flask_jwt_extended import JWTManager
from routes.devices import devices
from routes.data import data
from services.mqtt_handler import init_mqtt_handler


# define function to instantiate all the parts of the API
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # config file with .env vars
    db.init_app(app)  # init the db
    JWTManager(app)  # init JWT using custom key in .env
    CORS(app, resources={r"/api/*": {"origins": "*"}}) #CORS

    # Register Blueprints from routes
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(devices, url_prefix='/api')
    app.register_blueprint(data, url_prefix='/api')

    with app.app_context():
        # db context for app & access for mqtt
        db.create_all()
        init_mqtt_handler(app)
    
    return app


# Run app.
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
