<h4> Monitering and Automating IoT Devices </h4>

TODO:

[X] Reset web servers and load balancer.
[X] Setup DNS for new servers.
[X] UML Data Modelling for client device `ESP8266`.
[X] Create `Data model` classes.
[ ] Setup and test a possible configuration `Timeseries DB + NodeRED`.
[ ] Build API using the `Data Model` class objects.
[ ] Write basic init script for `ESP8266` clients compatible with API.
[ ] Run tests and troubleshooting for the ESP and a controlled circuit.

Continuous Tasks:
- Tests:
        - Write tests for `Data Model`
        - Write tests for `API Web_Server & Functions`

Data

`User`
      - ``username``
      - ``passwordHash``
      - ``[Devices]`` -
                       ``device``
                       - `deviceID`
                       - `Power`
                       - `[Readings]`