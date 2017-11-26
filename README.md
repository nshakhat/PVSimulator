PVSimulator
===========

PVSimulator generates a file with 1 day simulation which contains
the following information:
```
<timestamp> <V> <PV> <V+PV>
```

* "V" - Random value which simulates household electricity consumption. This value is generated
 using random.randrange(1, 9000)
* "PV" - PV simulated value. The library pvlib is used for that. See https://github.com/pvlib/pvlib-python
* "V + PV" - the sum of the two values

There are two main components:
1. Producer. Sends messages to a message broker (RabbitMQ) with random values. These values
mock a regular home power consumption.
2. Consumer. Consumes these messages, generates a Simulated PV value using pvlib library and
output results into the output file.


Requirements
============
* pvlib
* pika
* scipy
* pandas

How to prepare
==============
You can use tox to run the project.
After you run "tox" in the command line, three virtual environments will be
created in .tox folder: py27, py36 anb pep8. You can run the project in the following ways:
1. Python 2.7: .tox/py27/bin/simulate <args>
2. Python 3.6: .tox/py36/bin/simulate <args>

How to run the simulator
========================

```
usage: simulate    [-h] [--frequency fq] [--rabbit_host host]
                   [--rabbit_port port] [--rabbit_vhost vhost]
                   [--rabbit_username username] [--rabbit_password password]
                   start_date output

positional arguments:
  start_date            Start date for simulation in format "YYYY-mm-dd
                        HH:MM:SS"
  output                Output file

optional arguments:
  -h, --help            show this help message and exit
  --frequency fq        How often sampling should happen(in seconds). Default
                        is 3 seconds. The maximum value is 3600(1 hour), the
                        minimum value is 1 second.
  --rabbit_host host    RabbitMQ host. Default is 127.0.0.1
  --rabbit_port port    RabbitMQ port. Default is 5672
  --rabbit_vhost vhost  RabbitMQ vhost. Default is /
  --rabbit_username username
                        RabbitMQ username. Default is 'guest'
  --rabbit_password password
                        RabbitMQ password. Default is 'guest'
```
