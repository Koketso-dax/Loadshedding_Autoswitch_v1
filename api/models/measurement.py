"""
    Python module for data hypertables
"""
from models import db


class Measurement(db.Model):
    """ Class definition for measurement Hypertable """
    __tablename__ = 'measurements'
    __table_args__ = {'__timescaledb_hypertable__': {'time_column': 'timestamp', 'chunk_time_interval': '1 day'}}

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    timestamp = db.Column(db.DateTime())
    power_measurement = db.Column(db.Float)

    device = db.relationship('Device', backref='device_measurements')


"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to the database
conn = psycopg2.connect(
    dbname="your_database_name",
    user="your_username",
    password="your_password",
    host="your_host",
    port="your_port"
)

# Set the isolation level to AUTOCOMMIT
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor object
cur = conn.cursor()

# Execute the SQL query to create the hypertable
cur.execute("SELECT create_hypertable('measurements', 'timestamp', chunk_time_interval => INTERVAL '1 day')")

# Close the cursor and connection
cur.close()
conn.close()
"""