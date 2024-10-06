# Grow Control

_Grow Control_ is a piece of hardware and software to control and regulate 
conditions for an indoor garden.

The software is written in Python and runs on a Raspberry Pi. It performs the following tasks:

* soil moisture: regulate different pots from a single water reservoir
* temperature: measure it
* humidity: measure it
* fan: regulate it dependent on temperature and humidity
* light: control it
* provide an html interface to set all parameters
  and monitor current measurements (inclusive a graph of some parameters)
* send notification (e.g. mail) if any issues


## Required Python packages

```
pip3 install smbus2
pip3 install pimoroni-bme280==0.0.2
```

## Software module communication

![Communication](doc/communication.drawio.png "Communication")


## Hardware

![Schema](hardware/schema.drawio.png "Schema")

* ADC: Analog-Digital Converter ADS1115
* BME280
* Moisture Sensor: Capacitive Soil Moisture Sensor
* Water Level Sensor build with CD40106
* Relay Card 16 Channel
* Driver for Relay Card is an ULN2003
