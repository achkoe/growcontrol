#!/usr/bin/env python
"""Server to deliver fan and heater status and control the fan and heater."""

import logging
import os
import pathlib
import time
import datetime
import xmlrpc.client
from dotenv import dotenv_values
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import RPi.GPIO as GPIO
from servers.base import load_settings, get_loglevel
import configuration


IDENTITY = "fan_server.py v0.0.1"
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(get_loglevel("FAN_SERVER_LOGLEVEL"))


WAIT, RUN, DOWN = 0, 1, 2
START_AT_MINUTE = 5


GPIO.setmode(GPIO.BCM)


class Bridge():
    def __init__(self):
        self.settings = load_settings()
        self.sensors_proxy = xmlrpc.client.ServerProxy(
            f"http://localhost:{configuration.sensors_server_port}")
        # fan status
        self.fan_is_on = False
        self.previous_fan_is_on = not self.fan_is_on
        self.fan_mode_manual = False
        self.fan_on = False
        self.state = WAIT
        self.port_fan = configuration.port_fan
        GPIO.setup(configuration.port_fan, GPIO.OUT)
        
        # heater
        self.heater_is_on = False
        self.previous_heater_is_on = not self.heater_is_on
        self.heater_mode_manual = False
        self.heater_on = False
        self.port_heater = configuration.port_heater
        GPIO.setup(configuration.port_heater, GPIO.OUT)
        
        # exhaust air fan        
        self.fan_exhaust_air_is_on = True
        self.port_fan_exhaust_air = configuration.port_fan_exhaust_air
        GPIO.setup(configuration.port_fan_exhaust_air, GPIO.OUT)
        # switch fan for exhaust air on at start up
        GPIO.output(self.port_fan_exhaust_air, GPIO.LOW if self.fan_exhaust_air_is_on else GPIO.HIGH)
        
        # humidifier should go on if humidity is below humidity_low_level or if requested
        # but maximum of humidifier_minutes_in_hour
        self.humidifier_is_on = False
        self.humidifier_on = False
        self.previous_humidifier_is_on = not self.humidifier_is_on
        self.humidifier_time_on = None
        self.humidifier_last_time = None
        self.humidifier_start_time = None
        self.humidifier_mode_manual = False
        self.port_humidifier = configuration.port_humidifier
        GPIO.setup(configuration.port_humidifier, GPIO.OUT)


    def _execute(self):
        LOGGER.debug(f"state={self.state}")
        temperature = float(self.sensors_proxy.temperature())
        humidity = float(self.sensors_proxy.humidity())
        
        def ts(time_struct): return time_struct.tm_min

        # fan
        if self.fan_mode_manual is False:
            time_struct = time.localtime()
            # LOGGER.critical(f"state -> {self.state}, tm_min -> {time_struct.tm_sec}, START_AT_MINUTE -> {START_AT_MINUTE}")
            if self.state == WAIT:
                if ts(time_struct) >= START_AT_MINUTE and ts(time_struct) < START_AT_MINUTE + int(self.settings["fan_minutes_in_hour"]):
                    # start fan if minutes is between START_AT_MINUTE and START_AT_MINUTE + fan_minutes_in_hour 
                    LOGGER.info(f"3: state WAIT -> RUN")
                    self.fan_is_on = True
                    self.state = RUN
                else:
                    self.fan_is_on = False
            else:
                if ts(time_struct) == START_AT_MINUTE + int(self.settings["fan_minutes_in_hour"]):
                    # stop fan every hour + START_AT_MINUTE minutes + fan_minutes_in_hour
                    self.fan_is_on = False
                    self.state = WAIT
                    LOGGER.info(f"4:state: RUN -> WAIT")
        else:
            self.fan_is_on = self.fan_on
        if self.fan_is_on != self.previous_fan_is_on:
            self.previous_fan_is_on = self.fan_is_on
            GPIO.output(self.port_fan, GPIO.LOW if self.fan_is_on else GPIO.HIGH)
        
        # heater
        if self.heater_mode_manual is False:
            if temperature < float(self.settings["temperature_low_level"]):
                self.heater_is_on = True
                LOGGER.info(f"heater auto: ON (T={temperature})")
            elif temperature >= float(self.settings["temperature_high_level"]):
                self.heater_is_on = False
                LOGGER.info(f"heater auto: OFF (T={temperature})")
        else:
            self.heater_is_on = self.heater_on
        if self.heater_is_on != self.previous_heater_is_on:
            self.previous_heater_is_on = self.heater_is_on
            LOGGER.critical(f"heater_is_on -> {self.heater_is_on}")
            GPIO.output(self.port_heater, GPIO.HIGH if self.heater_is_on else GPIO.LOW)
            
        # humidifier
        if self.humidifier_mode_manual is False:
            now = datetime.datetime.now()
            humidity = 0
            if (humidity < float(self.settings["humidity_low_level"])) and (self.humidifier_start_time is None or (now - self.humidifier_start_time).total_seconds() >= 60 * 60):
                LOGGER.info("humidifier -> ON")
                self.humidifier_start_time = now
                self.humidifier_last_time = now
                self.humidifier_time_on = float(self.settings["humidifier_minutes_in_hour"])
                self.humidifier_is_on = True
                GPIO.output(self.port_humidifier, GPIO.HIGH)
                
            if self.humidifier_is_on and ((now - self.humidifier_last_time).total_seconds() >= 60):
                # decrement self.humidifier_time_on every minute
                self.humidifier_last_time = now
                self.humidifier_time_on = self.humidifier_time_on - 1
                LOGGER.info(f"humidifier_time_on -> {self.humidifier_time_on}")
                if self.humidifier_time_on <= 0:
                    LOGGER.info("humidifier -> OFF")
                    self.humidifier_is_on = False
                    GPIO.output(self.port_humidifier, GPIO.LOW)
        else:
            self.humidifier_is_on = self.humidifier_on
            self.humidifier_start_time = None
        if self.humidifier_is_on != self.previous_humidifier_is_on:
            self.previous_humidifier_is_on = self.humidifier_is_on
            LOGGER.info(f"humidifier_is_on -> {self.humidifier_is_on}")
            GPIO.output(self.port_humidifier, GPIO.HIGH if self.humidifier_is_on else GPIO.LOW)        

    def identity(self):
        return IDENTITY

    def get_fan(self):
        return "ON" if self.fan_is_on is True else "OFF"
    
    def get_fan_mode(self):
        return "Manual" if self.fan_mode_manual else "Auto"

    def set_fan(self, mode, fan_state):
        print(f"Brigde-set {mode} {fan_state}")
        self.fan_mode_manual = mode == "Manual"
        self.fan_on = fan_state.upper() == "ON"
        if self.fan_mode_manual is False:
            if self.state in [RUN, DOWN]:
                self.fan_is_on = True
        return "OK"
    
    def get_fan_exhaust_air(self):
        return "ON" if self.fan_exhaust_air_is_on else "OFF"

    def set_fan_exhaust_air(self, fan_exhaust_air_state):
        self.fan_exhaust_air_is_on = fan_exhaust_air_state.upper() == "ON"
        GPIO.output(self.port_fan_exhaust_air, GPIO.LOW if self.fan_exhaust_air_is_on else GPIO.HIGH)
        LOGGER.info(f"Fan Exhaust Air -> {self.fan_exhaust_air_is_on}")
        return "OK"
    
    def get_heater(self):
        return "ON" if self.heater_is_on else "OFF"
    
    def get_heater_mode(self):
        return "Manual" if self.heater_mode_manual else "Auto"
    
    def set_heater(self, mode, heater_state):
        print(f"Brigde-set {mode} {heater_state}")
        self.heater_mode_manual = mode == "Manual"
        self.heater_on = heater_state.upper() == "ON"
        return "OK"
        
    def get_humidifier(self):
        return "ON" if self.humidifier_is_on else "OFF"
    
    def get_humidifier_mode(self):
        return "Manual" if self.humidifier_mode_manual else "Auto"
    
    def set_humidifier(self, mode, humidifier_state):
        print(f"Brigde-set {mode} {humidifier_state}")
        self.humidifier_mode_manual = mode == "Manual"
        self.humidifier_on = humidifier_state.upper() == "ON"
        return "OK"
    
    def reload(self):
        self.settings = load_settings()
        LOGGER.setLevel(get_loglevel("FAN_SERVER_LOGLEVEL"))
        return "OK"


class TheServer(SimpleXMLRPCServer):
    def service_actions(self):
        self.instance._execute()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


if __name__ == "__main__":
    LOGGER.critical("FAN PROCESS STARTED")
    port = configuration.fan_server_port
    with TheServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(Bridge())
        server.serve_forever()
