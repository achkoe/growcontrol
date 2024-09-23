#!/usr/bin/env python
"""Server to gather data from other servers and deliver collected data."""

import logging
import copy
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from collections import deque
import time
from icecream import ic
from base import load_settings
import configuration


IDENTITY = "logdata_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)

MAX_LENGTH = 10


class Bridge():
    def __init__(self):
        self.settings = load_settings()
        self.sensors_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        self.pump_proxy_dict = copy.deepcopy(configuration.pump_moisture_dict)
        for key, value in self.pump_proxy_dict.items():
            self.pump_proxy_dict[key]["proxy"] = xmlrpc.client.ServerProxy(
                f"http://localhost:{value['pump']}")
            self.pump_proxy_dict[key]["moisture"] = deque(maxlen=MAX_LENGTH)
            self.pump_proxy_dict[key]["previous_moisture"] = -1
        self.temperature_humidity_queue = deque(maxlen=MAX_LENGTH)
        self.previous_time = -1
        self.previous_humidity = -1
        self.previous_temperature = -100

    def _execute(self):
        currenttime = time.time()
        if currenttime - self.previous_time > 60:
            # take atmost one sample in 60 seconds
            temperature = float(self.sensors_proxy.temperature())
            humidity = float(self.sensors_proxy.humidity())
            if (abs(humidity - self.previous_humidity) >= 1) or (abs(temperature - self.previous_temperature >= 0.5)) or True:
                self.temperature_humidity_queue.append(
                    (currenttime, temperature, humidity))
                # ic(self.temperature_humidity_queue)
                self.previous_humidity = humidity
                self.previous_temperature = temperature
            self.previous_time = currenttime

        for key in self.pump_proxy_dict:
            moisture = self.sensors_proxy.moisture(
                self.pump_proxy_dict[key]["channel"])
            if abs(self.pump_proxy_dict[key]["previous_moisture"] - moisture) >= 1:
                self.pump_proxy_dict[key]["moisture"].append(
                    (currenttime, moisture))
                self.pump_proxy_dict[key]["previous_moisture"] = moisture

    def identity(self):
        return IDENTITY

    def get(self):
        return list(self.temperature_humidity_queue), dict([(str(key), list(self.pump_proxy_dict[key]["moisture"])) for key in self.pump_proxy_dict])

    def set(self):
        return "OK"

    def reload(self):
        self.settings = load_settings()
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
