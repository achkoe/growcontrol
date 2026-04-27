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
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(get_loglevel("LOGDATA_SERVER_LOGLEVEL"))

MAX_LENGTH = 10
MAX_LENGTH = 2 * 24 * 60
INTERVAL = 60


class Bridge():
    def __init__(self):
        self.settings = load_settings()
        self.actors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.actors_server_port}")
        self.sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
        
        self.previous_data = dict()
        self.output = deque(maxlen=MAX_LENGTH)
        
    def _execute(self):
        try:
            data = self.sensors_proxy.get()
            data.update(self.actors_proxy.get())
        except Exception:
            return
        
        if data != self.previous_data:
            # print(data)
            self.previous_data = data
            data["time"] = time.time()
            self.output.append(data)

    def identity(self):
        return IDENTITY

    def get(self):
        statisticdata = dict(
            temperature_mean=statistics.mean([item["temperature"] for item in self.output]),
            temperature_min=min([item["temperature"] for item in self.output]),
            temperature_max=max([item["temperature"] for item in self.output]),
            humidity_mean=statistics.mean([item["humidity"] for item in self.output]),
            humidity_min=min([item["humidity"] for item in self.output]),
            humidity_max=max([item["humidity"] for item in self.output]))
        # returns 2 items:
        # 1st is list with dict of all gathered data
        # 2nd is dict with keys "temperature_mean", "temperature_min", "temperature_max", "humidity_mean", "humidity_min", "humidity_max"
        print(list(self.output), statisticdata)
        return list(self.output), statisticdata

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
