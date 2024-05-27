import json
from werkzeug.security import generate_password_hash, check_password_hash
from . import client

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user(username):
        query = f'SELECT * FROM "users" WHERE "username"=\'{username}\''
        result = client.query(query)
        points = list(result.get_points())
        if points:
            return points[0]
        return None

    def save(self):
        json_body = [
            {
                "measurement": "users",
                "tags": {
                    "username": self.username,
                },
                "fields": {
                    "password": self.password
                }
            }
        ]
        client.write_points(json_body)
