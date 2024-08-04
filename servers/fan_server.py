#!/usr/bin/env python
"""Server to deliver fan status and control the fan."""

import logging
import multiprocessing
import time
import atexit
import xmlrpc.client
from base import create_server, load_settings
import  configuration


IDENTITY = "fan_server.py v0.0.1"
inqueue = multiprocessing.Queue()
outqueue = multiprocessing.Queue()
logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGLEVEL = logging.CRITICAL
LOGGER = logging.getLogger()
LOGGER.setLevel(LOGLEVEL)


class Bridge():
   def identity(self):
       return IDENTITY
   
   def get(self):
      return self._communicate("get")
   
   def manual(self):
      print("Bridge-manual")
      return self._communicate("manual")

   def auto(self):
      print("Bridge-auto")
      return self._communicate("auto")

   def fanoff(self):
      print("Bridge-fanoff")
      return self._communicate("fanoff")

   def fanon(self):
      print("Bridge-fanon")
      return self._communicate("fanon")
   
   def reload(self):
      return self._communicate("reload")

   def _communicate(self, command):
      inqueue.put(command)
      return outqueue.get()


def process() -> None:
   logger = logging.getLogger()
   logger.setLevel(LOGLEVEL)
   logger.critical(f"FAN SERVER AT PORT {configuration.fan_server_port} STARTED")
   create_server(Bridge, configuration.fan_server_port)


def terminate():
   LOGGER.critical("TERMINATE FAN SERVER")    
   PROCESS.terminate()


PROCESS = multiprocessing.Process(target=process, args=())
PROCESS.start()
atexit.register(terminate)

WAIT, RUN = 0, 1
START_AT_MINUTE = 5

sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
# fan status
fan_status = False
fan_mode_manual = False
fan_on = False
state = WAIT

LOGGER.critical("FAN PROCESS STARTED")
settings = load_settings()

"""
fan_always_on   temp_high  humidity_high  timestart  timeend
1               X          X              X          X           -> ON
0               1          1              X          X           -> ON
0               0          1              X          X           -> ON
0               1          0              X          X           -> ON
0               0          0              1          0           -> ON
0               0          0              0          1           -> OFF
"""

while True:
   time.sleep(0.1)
   LOGGER.info(f"state={state}")
   temperature = float(sensors_proxy.temperature())
   humidity = float(sensors_proxy.humidity())
   
   if fan_mode_manual is False:
      if temperature > settings["temperature_high_level"] or humidity > settings["humidity_high_level"]:
         # start fan to reduce temperature or humidity
         fan_status = True
         state = WAIT
      else:
         time_struct = time.localtime()
         if state == WAIT:
            if time_struct.tm_min == START_AT_MINUTE:   
               # start fan every hour + START_AT_MINUTE minutes
               LOGGER.info(f"state 0 -> 1")
               fan_status = True
               state = RUN
            else:
               fan_status = False
         else:
            if time_struct.tm_min == START_AT_MINUTE + settings["fan_minutes_in_hour"]:
               # stop fan every hour + START_AT_MINUTE minutes + fan_minutes_in_hour
               fan_status = False
               state = WAIT
               LOGGER.info(f"state 1 -> 0")
   else:
      fan_status = fan_on
         
   if not inqueue.empty():
      query = inqueue.get()
      LOGGER.info(f"query -> {query!r}")
      if query == "get":
          reply = "ON" if fan_status is True else "OFF"
          outqueue.put(reply)
      elif query == "reload":
         settings = load_settings()
         outqueue.put("reload-OK")
      elif query == "manual":
         fan_mode_manual = True
         fan_on = False
         outqueue.put("manual-OK")
      elif query == "auto":
         fan_mode_manual = False
         outqueue.put("auto-OK")
      elif query == "fanon":
         fan_on = True
         outqueue.put("fanon-OK")
      elif query == "fanoff":
         fan_on = False
         outqueue.put("fanoff-OK")
      else:
          LOGGER.info(f"out <- ?{str(query)}")
          outqueue.put(f"?{str(query)}")