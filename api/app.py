from flask import Flask
from config import Config
from models import db
from flask_jwt_extended import JWTManager
from routes.auth import auth
from routes.devices import devices
from routes.data import data
from services.mqtt_handler import init_mqtt_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(devices, url_prefix='/api')
    app.register_blueprint(data, url_prefix='/api')

    with app.app_context():
        db.create_all()

    init_mqtt_client(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
