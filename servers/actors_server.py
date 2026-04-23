#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""

import json
import logging
import os
import pathlib
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from dotenv import dotenv_values

from base import load_settings, get_loglevel
import configuration
import  servers.actors_driver as driver


IDENTITY = "actor_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("ACTOR_SERVER_LOGLEVEL"))
    
    
class ActorOnOff():
    def __init__(self):
        self.on = True
        self.mode = "auto"
        
    def set_on(self, on: bool):
        if self.mode == "auto":
            return
        self.on = on
    
    def set_mode(self, mode: str):
        if mode in ["auto", "manual"]:
            self.mode = mode
        else:
            print(f"ERROR: unknown mode: {mode!r}")


actorExhaustAirFan = ActorOnOff()
actorLight = ActorOnOff()

class Bridge():
    def __init__(self):
        self.settings = load_settings()
        self._execute()

    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("SENSOR_SERVER_LOGLEVEL"))
        return "OK"

    def identity(self):
        return IDENTITY
        
    def _execute(self):
        pass
            
    def get(self):
        return {
            "light-on": actorLight.on,
            "light-mode": actorLight.mode,
            "heater-on": True,
            "heater-mode": "auto",
            "fan-on": True,
            "fan-mode": "auto",
            "humidifier-on": False,
            "humidifier-mode": "auto",
            "exhaustairfan-on": actorExhaustAirFan.on,
            "exhaustairfan-mode": actorExhaustAirFan.mode,
        }
        
    def set(self, element, action):
        print(f"actors_server:set: element={element}, action={action}")
        actor = {
            "exhaustairfan": actorExhaustAirFan,
            "light": actorLight
        }.get(element, None)
        if actor is None:
            print("ERROR:set: unknown element: {element!r}")
            return
        if action == "s":
            actor.set_on(not actor.on)
        elif action == "a":
            actor.set_mode("auto" if actor.mode == "manual" else "manual")
        else:
            print("ERROR:set: unknown action: {action!r}")
        return 0
            
        
class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


LOGGER.critical("ACTOR PROCESS STARTED")
bridge = Bridge()
port = configuration.actors_server_port
with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()
    server.register_instance(bridge)
    server.serve_forever()
