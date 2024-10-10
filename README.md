<h4> Loadshedding Autoswitch </h4>

<h6> Monitering anomalies in your power system.</h6>

[Loadshedding Autoswitch Article](https://medium.com/@lanchaster.k/loadshedding-auto-switch-3957d99c7d93).

<p> This project is aimed at creating a highly available, low latency API to communicate with IoT devices to monitor metrics such as energy generation & usage in order to leverage the information for use in various applications such as power failure detection and energy trading. The UI has not been deployed however, the api is available at web-01.koketsodiale.tech/api.</p>

<h6> Installation </h6>

The application has two main components:

- The API: which is a Flask Application coupled with an MQTT Broker and a PostgreSQL database.
- The Client: (optional), a NextJS application which interacts with the API and has features such as a Dashboard.

To install the API you will need a Linux VM (Ubuntu V20.04) NB: this application has only been tested in the above stated machine.

- Python v3.8 (with pip)
- PostgreSQL Server (@main13)
- MQTT Broker (v 2.0.11)
- Timescaledb (core)

Then run requirements.txt

Once you have installed these packages, you can run this app via app.py.

If you want to run the client as well, you can install node v21.

Then run npm install while in the /client directory.

You can then run a dev server using npm run dev.
