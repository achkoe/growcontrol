#!/usr/bin/env python
"""Server to deliver temperature and humidity over xmlrpc."""

import json
import logging
import os
from datetime import datetime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from dotenv import dotenv_values
from oncalendar import BaseIterator
from base import load_settings, get_loglevel
import configuration
import  servers.actors_driver as driver


IDENTITY = "actor_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("ACTOR_SERVER_LOGLEVEL"))
    
    
class Actor():
    def __init__(self, name):
        self.name = name
        self.on_manual = True
        self.on_auto = True
        self.on = True
        self.mode = "auto"
        self.on_time_it = None
        self.off_time_it = None
        self.on_time = None
        self.off_time = None
        
    def set_on(self, on: bool):
        if self.mode == "auto":
            return
        self.on_manual = on
    
    def set_mode(self, mode: str):
        if mode in ["auto", "manual"]:
            self.mode = mode
        else:
            print(f"ERROR: unknown mode: {mode!r}")
            
    def set_on_time(self, t):
        self.on_time_it = BaseIterator(t, datetime.now())
        self.on_time = next(self.on_time_it)

    def set_off_time(self, t):
        self.off_time_it = BaseIterator(t, datetime.now())
        self.off_time = next(self.off_time_it)
        
    def execute(self):
        """
        """
        now = datetime.now()
        message = "{}: t={} : now >= on_time={} : now >= off_time={}".format(
            self.name,
            now.isoformat(),
            now >= self.on_time,
            now >= self.off_time,
        )
        if now >= self.on_time:
            self.on_auto = True
            self.on_time = next(self.on_time_it)
        if now >= self.off_time:
            self.on_auto = False
            self.off_time = next(self.off_time_it)
        LOGGER.info("{} : on_auto={}".format(message, self.on_auto))
        if self.mode == "auto":
            self.on = self.on_auto
        else:
            self.on = self.on_manual
        driver.set(self.name, self.on)
        

actorMap = dict((key, Actor(key)) for key in ["exhaustairfan", "fan", "light"])


class Bridge():
    def __init__(self):
        self.reload()
        self._execute()

    def reload(self):
        self.settings = load_settings()
        for key in actorMap:
            actorMap[key].set_on_time(self.settings[key]["ontime"]["value"])
            actorMap[key].set_off_time(self.settings[key]["offtime"]["value"])
        LOGGER.setLevel(get_loglevel("ACTOR_SERVER_LOGLEVEL"))
        return "OK"

    def identity(self):
        return IDENTITY
        
    def _execute(self):
        for key in actorMap:
            actorMap[key].execute()
            
    def get(self):
        return {
            "light-on": actorMap["light"].on,
            "light-mode": actorMap["light"].mode,
            "heater-on": True,
            "heater-mode": "auto",
            "fan-on": actorMap["fan"].on,
            "fan-mode": actorMap["fan"].mode,
            "humidifier-on": False,
            "humidifier-mode": "auto",
            "exhaustairfan-on": actorMap["exhaustairfan"].on,
            "exhaustairfan-mode": actorMap["exhaustairfan"].mode,
        }
        
    def set(self, element, action):
        print(f"actors_server:set: element={element}, action={action}")
        actor = actorMap.get(element, None)
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
