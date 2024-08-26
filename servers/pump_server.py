#!/usr/bin/env python
"""Server to deliver pump status and control the pump."""

import logging
import argparse
import time
import os
import xmlrpc.client
from dotenv import load_dotenv
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import RPi.GPIO as GPIO

from base import load_settings
import configuration


load_dotenv()


IDENTITY = "pump_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = int(os.getenv("PUMP_SERVER_LOGLEVEL", logging.CRITICAL))
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


WAIT, RUN, MANUAL = 0, 1, 2

GPIO.setmode(GPIO.BCM)


class Bridge:
    def __init__(self, moisture_channel: int, pump_gpio: int):
        self.settings = load_settings()
        self.sensor_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        self.moisture_channel = moisture_channel
        self.pump_gpio = pump_gpio
        GPIO.setup(pump_gpio, GPIO.OUT)
        self.pump_mode_manual = False
        self.pump_on = False
        self.state = WAIT
        self.wait_between = 60  # wait seconds between two pump shots
        self.shot_time = 3      # time to for one single pump in seconds
        self.last_time = -1

    def _execute(self):
        waterlevel = int(self.sensor_proxy.waterlevel())
        # waterlevel 1 means out of water
        if waterlevel > 0:
            # permit the pump to fall dry
            self.pump_on = False
            GPIO.output(self.pump_gpio, GPIO.LOW)
            LOGGER.info("pump OFF")
            return
        if self.pump_mode_manual is True:
            GPIO.output(self.pump_gpio,
                        GPIO.HIGH if self.pump_on else GPIO.LOW)
            LOGGER.info("pump {}".format("ON" if self.pump_on else "OFF"))
            return
        moisture = float(self.sensor_proxy.moisture(self.moisture_channel))
        if self.state == WAIT:
            if moisture < float(self.settings["moisture_low_level"]):
                LOGGER.info(
                    f"state: WAIT -> RUN (moisture={moisture}, moisture_low_level={float(self.settings['moisture_low_level'])})")
                self.state = RUN
        if self.state == RUN:
            if moisture >= float(self.settings["moisture_ok_level"]):
                self.pump_on = False
                GPIO.output(self.pump_gpio, GPIO.LOW)
                LOGGER.info("state: RUN -> WAIT")
                self.state = WAIT
                return
            t = time.time()
            if self.pump_on:
                if t - self.last_time >= self.shot_time:
                    LOGGER.info("pump OFF")
                    self.pump_on = False
                    GPIO.output(self.pump_gpio, GPIO.LOW)
                    self.last_time = t
            else:
                if t - self.last_time >= self.wait_between:
                    LOGGER.info("pump ON")
                    self.pump_on = True
                    GPIO.output(self.pump_gpio, GPIO.HIGH)
                    self.last_time = t

    def identity(self):
        return IDENTITY

    def get(self):
        state = "MANUAL" if self.pump_mode_manual is True else ["WAIT", "RUN"][self.state]
        return "{} ({})".format(state, "ON" if self.pump_on else "OFF")

    def set(self, mode, pump_state):
        print(f"Brigde-set {mode} {pump_state}")
        self.pump_mode_manual = mode == "Manual"
        self.pump_on = pump_state == "On"
        return "OK"

    def reload(self):
        self.settings = load_settings()
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
                configuration.pump_moisture_dict[args.number]["gpio"]
            )
        )
        server.serve_forever()
