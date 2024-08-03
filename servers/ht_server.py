#!/usr/bin/env python
"""Server to deliver temperature and humidity over dbus."""

# Based on http://stackoverflow.com/questions/22390064/use-dbus-to-just-send-a-message-in-python


import multiprocessing
import time
import logging
import atexit
from gi.repository import GLib
from pydbus import SessionBus

IDENTITY = "ht_server.py v0.0.1"
loop = GLib.MainLoop()
send_queue = multiprocessing.Queue()
recv_queue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)


def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
    # So far just for testing
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)
    logger.critical("HT PROCESS STARTED")
    temperature = 24.23456
    humidity = 48.1
    while True:
        time.sleep(0.01)
        if not inqueue.empty():
            query = inqueue.get()
            logger.info(f"query -> {query!r}")
            if query == "temperature":
                logger.info(f"out <- {temperature}")
                outqueue.put(temperature)
            elif query == "humidity":
                logger.info(f"out <- {humidity}")
                outqueue.put(humidity)
            elif query.startswith("settemperature"):
                temperature = float(query[len("settemperature"):])
                outqueue.put("OK")
            else:
                logger.info(f"out <- ?{str(query)}")
                outqueue.put(f"?{str(query)}")

		
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.CRITICAL)

PROCESS = multiprocessing.Process(target=process, args=(send_queue, recv_queue))
PROCESS.start()


def terminate():
   LOGGER.critical("TERMINATE HT PROCESS")    
   PROCESS.terminate()
   

atexit.register(terminate)


class TheDBUSService(object):
   """
      <node>
         <interface name='net.ak.pydbus.htserver'>
            <method name='identity'>
               <arg type='s' name='response' direction='out'/>
            </method>
            <method name='temperature'>
               <arg type='s' name='response' direction='out'/>
            </method>
            <method name='humidity'>
               <arg type='s' name='response' direction='out'/>
            </method>
            <method name='quit'/>
            <method name="settemperature">
               <arg type='d' name='a' direction='in'/>
               <arg type='s' name='response' direction='out'/>
            </method>
         </interface>
      </node>
	"""
   def quit(self):
     """removes this object from the DBUS connection and exits"""
     loop.quit()

   def settemperature(self, value):
       LOGGER.info(("settemperature", repr(value), type(value)))
       return self._communicate(f"settemperature{value}")
   
   def identity(self):
       return IDENTITY
   
   def temperature(self):
      LOGGER.info("temperature")
      return "{:4.1f}".format(self._communicate("temperature"))       

   def humidity(self):
      LOGGER.info("humidity")
      return "{:4.1f}".format(self._communicate("humidity")       )
   
   def _communicate(self, command):
      global PROCESS
      send_queue.put(command)
      return recv_queue.get()
	

bus = SessionBus()
bus.publish("net.ak.pydbus.htserver", TheDBUSService())
loop.run()
