"""
    measurements.py
"""
import psycopg2

class Measurement:
    def __init__(self, device_id, timestamp, power_measurement):
        self.device_id = device_id
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

        # Check if the measurements table exists
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'measurements')")
        table_exists = cur.fetchone()[0]

        if not table_exists:
            # Create the measurements table with a foreign key constraint to the devices table
            cur.execute("""
                CREATE TABLE measurements (
                    measurement_id SERIAL PRIMARY KEY,
                    device_id INTEGER NOT NULL REFERENCES devices(device_id),
                    timestamp TIMESTAMPTZ NOT NULL,
                    power_measurement FLOAT NOT NULL
                );
            """)
            conn.commit()

        # Insert the measurement data into the measurements table
        cur.execute("INSERT INTO measurements (device_id, timestamp, power_measurement) VALUES (%s, %s, %s);",
                    (self.device_id, self.timestamp, self.power_measurement))
        conn.commit()

        cur.close()
        conn.close()

    @staticmethod
    def create_continuous_aggregates():
        conn = psycopg2.connect(
            dbname="autoswitch",
            user="postgres",
            password="password",
            host="localhost",
            port="5433"
        )
        cur = conn.cursor()

        # Populate the materialized views with data
        cur.execute("REFRESH MATERIALIZED VIEW kwh_day_by_day")
        cur.execute("REFRESH MATERIALIZED VIEW kwh_hour_by_hour")

        conn.commit()
        cur.close()
        conn.close()
