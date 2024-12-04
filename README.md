<h4> Loadshedding Autoswitch </h4>

<h6> Monitering anomalies in your power system.</h6>

[Loadshedding Autoswitch Article](https://medium.com/@lanchaster.k/loadshedding-auto-switch-3957d99c7d93).

<p> This project is aimed at creating a highly available, low latency API to communicate with IoT devices to monitor metrics such as energy generation & usage in order to leverage the information for use in various applications such as power failure detection and energy trading. The UI has not been deployed however, the api is available at web-01.koketsodiale.tech/api.</p>

<h6> Installation </h6>

Componets:

- Flask Application for User and Device Management.
- MQTT Broker and Hub to Get sensor data and control devices.
- PostgreSQL database with timescaledb plugin enabled.
- The Client: NextJS Application which has all UI components.

- Tested on Ubuntu 20+

- Python v3.8 (with pip)
- PostgreSQL Server (@main13)
- MQTT Broker (v 2.0.11)
- Timescaledb (core)

Then run requirements.txt

Once you have installed these packages, you can run this app via app.py.

If you want to run the client as well, you can install node v21.

Then run npm install while in the /client directory.

You can then run a dev server using npm run dev.
