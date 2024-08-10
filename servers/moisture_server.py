#!/usr/bin/env python
"""Server to deliver soil moisture over xmlrpc."""


import logging
import argparse
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from base import load_settings
import configuration


IDENTITY = "moisture_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge:
    def __init__(self):
        self._moisture = 10
        self.settings = load_settings()

    def _execute(self):
        pass

    def identity(self):
        return IDENTITY

    def moisture(self):
        LOGGER.info("moisture")
        return "{:d}".format(self._moisture)

    def setmoisture(self, value):
        LOGGER.info(("setmoisture", repr(value), type(value)))
        self._moisture = int(value)
        return self._moisture

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
    port = configuration.moisture_server_port_dict[args.number]["moisture"]
    LOGGER.critical(f"MOISTURE PROCESS STARTED AT PORT {port}")
    with TheServer(
        ("localhost", port), requestHandler=RequestHandler, logRequests=False
    ) as server:
        server.register_introspection_functions()
        server.register_instance(Bridge())
        server.serve_forever()
