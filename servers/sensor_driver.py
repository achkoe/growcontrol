from types import SimpleNamespace
import RPi.GPIO as GPIO
import smbus2
from bme280 import BME280
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import configuration
from configuration import port_waterlow, port_watermedium, port_waterhigh

instruments = SimpleNamespace()

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([port_waterlow, port_watermedium, port_waterhigh], GPIO.IN)

    # initialize BME280 sensor for temperature and humidity
    instruments.bme280 = BME280(i2c_dev=smbus2.SMBus(1))

    # Create the ADC object using the I2C bus
    instruments.ads = ADS.ADS1015(busio.I2C(board.SCL, board.SDA))
    # settings for moisture
    # max value ~17390: dry
    # min value ~7470: wet
    instruments._min = 7500
    instruments._max = 17000
    instruments._slope = (100.0 - 0.0) / (instruments._min - instruments._max)
    instruments._offset = - instruments._slope * instruments._max


def get():
    data = dict()
    data["temperature"] = instruments.bme280.get_temperature()
    data["humidity"] = instruments.bme280.get_humidity()
    waterlevels = [GPIO.input(pin) for pin in (port_waterlow, port_watermedium, port_waterhigh)]
    # [1, 1, 1] -> water level is below low marker
    # [0, 1, 1] -> water is between low and medium marker
    # [0, 0, 1] -> water is between medium and high marker
    # [0, 0, 0] -> water is between above high marker
    if waterlevels == [0, 0, 0]:
        data["waterlevel"] = 0        # critical
    elif waterlevels == [1, 0, 0]:
        data["waterlevel"] = 1        # low
    elif waterlevels == [1, 1, 0]:
        data["waterlevel"] = 2        # medium
    elif waterlevels == [1, 1, 1]:  
        data["waterlevel"] = 3        # full
    else:
        # this should be impossible, therefore set to critical
        data["waterlevel"] = 0
        
    data["moisture"] = []
    for key in configuration.moisture_dict:
        adc = AnalogIn(instruments.ads, configuration.moisture_dict[key]["channel"])
        rval = adc.value
        rval = min(instruments._max, rval)      # set upper limit
        rval = max(instruments._min, rval)      # set lower limit
        rval = instruments._slope * rval + instruments._offset
        data["moisture"].append(rval)