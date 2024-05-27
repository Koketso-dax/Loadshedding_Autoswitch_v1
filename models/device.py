from . import client

class Device:
    def __init__(self, device_id, power, readings, user_id):
        self.device_id = device_id
        self.power = power
        self.readings = readings
        self.user_id = user_id

    @staticmethod
    def get_devices_by_user(user_id):
        query = f'SELECT * FROM "device_readings" WHERE "user_id"=\'{user_id}\''
        result = client.query(query)
        devices = list(result.get_points())
        return devices

    def save(self):
        json_body = [
            {
                "measurement": "device_readings",
                "tags": {
                    "device_id": self.device_id,
                    "user_id": self.user_id,
                },
                "fields": {
                    "power": self.power,
                    **self.readings
                }
            }
        ]
        client.write_points(json_body)
