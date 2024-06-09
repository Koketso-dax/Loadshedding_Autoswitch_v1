from influxdb import InfluxDBClient

# instantiate a server Flask or FastAPI ?

client = InfluxDBClient(host='web-01.koketsodiale.tech', port=8086)

# define endpoint for basic functions