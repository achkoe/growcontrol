#!/usr/bin/env python
"""Server to deliver pump status and control the pump."""

import logging
import argparse
import time
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from base import load_settings
import configuration


IDENTITY = "moisture_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.INFO
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


WAIT, RUN = 0, 1


class Bridge:
    def __init__(self, moisture_server_port: int):
        self.settings = load_settings()
        self.moisture_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{moisture_server_port}")
        self.sensor_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        self.pump_mode_manual = False
        self.pump_on = False
        self.state = WAIT
        self.wait_between = 6  # wait between two pump shots
        self.shot_time = 1     # time to for one single pump
        self.last_time = -1

    def _execute(self):
        waterlevel = float(self.sensor_proxy.waterlevel())
        if waterlevel <= float(self.settings["waterlevel_low"]):
            # permit the pump to fall dry
            self.pump_on = False
            LOGGER.info("pump OFF")
            return
        moisture = float(self.moisture_proxy.moisture())
        if self.state == WAIT:
            if moisture < float(self.settings["moisture_low_level"]):
                LOGGER.info(
                    f"state: WAIT -> RUN (moisture={moisture}, moisture_low_level={float(self.settings['moisture_low_level'])})")
                self.state = RUN
        if self.state == RUN:
            if moisture >= float(self.settings["moisture_ok_level"]):
                self.pump_on = False
                LOGGER.info("state: RUN -> WAIT")
                self.state = WAIT
                return
            t = time.time()
            if self.pump_on:
                if t - self.last_time >= self.shot_time:
                    LOGGER.info("pump OFF")
                    self.pump_on = False
                    self.last_time = t
            else:
                if t - self.last_time >= self.wait_between:
                    LOGGER.info("pump ON")
                    self.pump_on = True
                    self.last_time = t

    def identity(self):
        return IDENTITY

    def get(self):
        return "{} ({})".format(["WAIT", "RUN"][self.state], "ON" if self.pump_on else "OFF")

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
        choices=configuration.moisture_server_port_dict.keys(),
        type=int,
        help=f"server number, one of {configuration.moisture_server_port_dict.keys()}",
    )
    args = parser.parse_args()
    port = configuration.moisture_server_port_dict[args.number]["pump"]
    LOGGER.critical(f"PUMP PROCESS STARTED AT PORT {port}")
    with TheServer(
        ("localhost", port), requestHandler=RequestHandler, logRequests=False
    ) as server:
        server.register_introspection_functions()
        server.register_instance(
            Bridge(
                configuration.moisture_server_port_dict[args.number]["moisture"])
        )
        server.serve_forever()
