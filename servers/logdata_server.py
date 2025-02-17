#!/usr/bin/env python
"""Server to gather data from other servers and deliver collected data."""

import logging
import copy
import os
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from collections import deque
import statistics
import time
from base import load_settings, get_loglevel
import configuration


IDENTITY = "logdata_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("LOGDATA_SERVER_LOGLEVEL"))

MAX_LENGTH = 10
MAX_LENGTH = 2 * 24 * 60


class Bridge():
    def __init__(self):
        self.settings = load_settings()
        self.fan_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.fan_server_port}")
        self.sensors_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        self.pump_proxy_dict = copy.deepcopy(configuration.pump_moisture_dict)
        for key, value in self.pump_proxy_dict.items():
            self.pump_proxy_dict[key]["proxy"] = xmlrpc.client.ServerProxy(
                f"http://localhost:{value['pump']}")
            self.pump_proxy_dict[key]["moisture"] = deque(maxlen=MAX_LENGTH)
            self.pump_proxy_dict[key]["pump"] = -1
        self.output_queue = deque(maxlen=MAX_LENGTH)
        self.previous_time = -1
        self.previous_fan = -1
        self.previous_heater = -1
        self.previous_humidifier = -1

    def _execute(self):
        interval = 60
        currenttime = time.time()
        fan = 1 if self.fan_proxy.get_fan() == "ON" else 0
        heater = 1 if self.fan_proxy.get_heater() == "ON" else 0
        humidifier = 1 if self.fan_proxy.get_humidifier() == "ON" else 0
        temperature = float(self.sensors_proxy.temperature())
        humidity = float(self.sensors_proxy.humidity())

        if (fan != self.previous_fan) or (heater != self.previous_heater) or (humidifier != self.previous_humidifier) or (currenttime - self.previous_time > interval):
            # take atmost one sample in 60 seconds
            self.output_queue.append(
                (currenttime, temperature, humidity, fan, heater, humidifier))
            # ic(self.output_queue)
            self.previous_fan = fan
            self.previous_heater = heater
            self.previous_humidifier = humidifier

        for key in self.pump_proxy_dict:
            pump = 1 if self.pump_proxy_dict[key]["proxy"].get() == "ON" else 0
            if (pump != self.pump_proxy_dict[key]["pump"]) or (currenttime - self.previous_time > interval):
                moisture = self.sensors_proxy.moisture(
                    self.pump_proxy_dict[key]["channel"])
                self.pump_proxy_dict[key]["moisture"].append(
                    (currenttime, moisture, pump))
                self.pump_proxy_dict[key]["pump"] = pump

        if (currenttime - self.previous_time > interval):
            self.previous_time = currenttime

    def identity(self):
        return IDENTITY

    def get(self):
        # returns 3 items:
        # 1st is list with tuples (time, temperature, humidity, fan, heater, humidifier)
        # 2nd is dict with keys <pump> and tuples (time, moisture, pump)
        # 3rd is dict with keys "temperature_mean", "temperature_min", "temperature_max", "humidity_mean", "humidity_min", "humidity_max"
        return list(self.output_queue), \
            dict([(str(key), list(self.pump_proxy_dict[key]["moisture"])) for key in self.pump_proxy_dict]), \
            dict(
                temperature_mean=statistics.mean([item[1] for item in self.output_queue]),
                temperature_min=min([item[1] for item in self.output_queue]),
                temperature_max=max([item[1] for item in self.output_queue]),
                humidity_mean=statistics.mean([item[2] for item in self.output_queue]),
                humidity_min=min([item[2] for item in self.output_queue]),
                humidity_max=max([item[2] for item in self.output_queue]))

    def set(self):
        return "OK"

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("LOGDATA_SERVER_LOGLEVEL"))
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == "__main__":
    LOGGER.critical("LOGDATA PROCESS STARTED")
    port = configuration.logdata_server_port
    with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(Bridge())
        server.serve_forever()
