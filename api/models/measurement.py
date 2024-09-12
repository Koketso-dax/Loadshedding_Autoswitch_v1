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
                )
            """)
            conn.commit()

        # Insert the measurement data into the measurements table
        cur.execute("INSERT INTO measurements (device_id, timestamp, power_measurement) VALUES (%s, %s, %s)",
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

        # Create continuous aggregate for energy consumption by day
        cur.execute("""
            CREATE MATERIALIZED VIEW kwh_day_by_day(time, device_name, value)
                WITH (timescaledb.continuous) AS
            SELECT time_bucket('1 day', timestamp, 'UTC') AS "time",
                   device_name,
                   round((last(power_measurement, timestamp) - first(power_measurement, timestamp)) * 100.) / 100. AS value
            FROM measurements
            GROUP BY 1, 2;
        """)

        # Add refresh policy for energy consumption by day
        cur.execute("""
            SELECT add_continuous_aggregate_policy('kwh_day_by_day',
               start_offset => NULL,
               end_offset => INTERVAL '1 hour',
               schedule_interval => INTERVAL '1 hour');
        """)

        # Create continuous aggregate for energy consumption by hour
        cur.execute("""
            CREATE MATERIALIZED VIEW kwh_hour_by_hour(time, device_name, value)
                WITH (timescaledb.continuous) AS
            SELECT time_bucket('1 hour', timestamp, 'UTC') AS "time",
                   device_name,
                   round((last(power_measurement, timestamp) - first(power_measurement, timestamp)) * 100.) / 100. AS value
            FROM measurements
            GROUP BY 1, 2;
        """)

        # Add refresh policy for energy consumption by hour
        cur.execute("""
            SELECT add_continuous_aggregate_policy('kwh_hour_by_hour',
               start_offset => NULL,
               end_offset => INTERVAL '1 hour',
               schedule_interval => INTERVAL '1 hour');
        """)

        conn.commit()
        cur.close()
        conn.close()
