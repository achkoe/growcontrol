#!/usr/bin/env python
"""Server to deliver pump status and control the pump."""

import logging
import argparse
import time
import os
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import RPi.GPIO as GPIO
from servers.base import load_settings, get_loglevel
import configuration


IDENTITY = "pump_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("PUMP_SERVER_LOGLEVEL"))


OFF, ON = False, True

GPIO.setmode(GPIO.BCM)


class Bridge:
    def __init__(self, moisture_channel: int, pump_gpio: int, milliliter_per_second: int):
        # pump_milliliter_per_second
        # pump_amount
        # pump_check_interval
        self.settings = load_settings()
        self.sensor_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        self.moisture_channel = moisture_channel
        self.pump_gpio = pump_gpio
        GPIO.setup(pump_gpio, GPIO.OUT)
        self.pump_state = OFF
        self.pump_request_on = False
        self.milliliter_per_second = milliliter_per_second
        self.pump_on_time = self.settings["pump_amount"] / self.milliliter_per_second
        LOGGER.info(f"pump on time -> {self.pump_on_time}")
        self.last_time = None
        self.start_time = None

    def _execute(self):
        waterlevel = int(self.sensor_proxy.waterlevel())
        # waterlevel 0 means out of water
        if waterlevel == 0:
            # permit the pump to fall dry
            self.pump_state = OFF
            GPIO.output(self.pump_gpio, GPIO.LOW)
            LOGGER.info(f"waterlevel is {waterlevel} -> pump {self.pump_state}")
            return
        
        if self.pump_state == OFF:
            if self.pump_request_on is True:
                # request to turn pump on, without any conditions
                self.pump_state = ON
                self.start_time = time.time()
                LOGGER.info(f"pump_request_on is {self.pump_request_on} -> pump {self.pump_state}")
                self.pump_request_on = False
                self.last_time = time.time()
            else:
                current_time = time.time()
                if (self.last_time is None) or (current_time - self.last_time > self.settings["pump_check_interval"] * 60 * 60):
                # if (self.last_time is None) or (current_time - self.last_time > self.settings["pump_check_interval"]):
                    self.last_time = current_time
                    moisture = float(self.sensor_proxy.moisture(self.moisture_channel))
                    if moisture < float(self.settings["moisture_low_level"]):
                        self.pump_state = ON
                        self.start_time = time.time()
                        LOGGER.info(f"moisture is {moisture} -> pump {self.pump_state}")
        if self.pump_state == ON:
            current_time = time.time()
            if current_time - self.start_time >= self.pump_on_time:
                self.pump_state = OFF
                self.last_time = current_time
                LOGGER.info(f"pump {self.pump_state}")
        
        GPIO.output(self.pump_gpio, GPIO.HIGH if self.pump_state is True else GPIO.LOW)
                
    def identity(self):
        return IDENTITY

    def get(self):
        return "ON" if self.pump_state is ON else "OFF"
    
    def get_state(self):
        return "-" if self.last_time is None else time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime(self.last_time))

    def set(self, pump_state):
        print(f"Brigde-set {pump_state}")
        self.pump_request_on = pump_state == "On"
        return "OK"

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("PUMP_SERVER_LOGLEVEL"))
        self.pump_on_time = self.settings["pump_amount"] / self.milliliter_per_second
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "number",
        choices=configuration.pump_moisture_dict.keys(),
        type=int,
        help=f"server number, one of {configuration.pump_moisture_dict.keys()}",
    )
    args = parser.parse_args()
    port = configuration.pump_moisture_dict[args.number]["pump"]
    LOGGER.critical(f"PUMP PROCESS STARTED AT PORT {port}")
    with TheServer(
        ("localhost", port), requestHandler=RequestHandler, logRequests=False
    ) as server:
        server.register_introspection_functions()
        server.register_instance(
            Bridge(
                configuration.pump_moisture_dict[args.number]["channel"],
                configuration.pump_moisture_dict[args.number]["gpio"],
                configuration.pump_moisture_dict[args.number]["milliliter_per_second"],
            )
        )
        server.serve_forever()
