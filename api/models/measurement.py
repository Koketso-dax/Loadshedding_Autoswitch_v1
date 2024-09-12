"""
    Python module for data hypertables
"""
import psycopg2

class Measurement:
    def __init__(self, device_name, timestamp, power_measurement):
        self.device_name = device_name
        self.timestamp = timestamp
        self.power_measurement = power_measurement

    def save(self):
        conn = psycopg2.connect(
            dbname="autoswitch",
            user="postgres",
            password="password",
            host="localhost",
            port="5433"
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO measurements (device_name, timestamp, power_measurement) VALUES (%s, %s, %s)",
                    (self.device_name, self.timestamp, self.power_measurement))
        conn.commit()
        cur.close()
        conn.close()
