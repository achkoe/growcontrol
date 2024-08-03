#!/usr/bin/env python
"""Server to deliver fan status and control the fan."""

import logging
import multiprocessing
import time
import atexit
from gi.repository import GLib
from pydbus import SessionBus


IDENTITY = "fan_server.py v0.0.1"
loop = GLib.MainLoop()
send_queue = multiprocessing.Queue()
recv_queue = multiprocessing.Queue()
logging.basicConfig(format="%(module)s:%(levelname)s:%(message)s", level=logging.DEBUG)



def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
    # So far just for testing
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)
    logger.critical("FAN PROCESS STARTED")
    
    bus = SessionBus()
    
    # server for temperature and humidity
    ht_server = bus.get("net.ak.pydbus.htserver")
    # fan status
    fan_status = True

    while True:
        time.sleep(0.01)
        temperature = float(ht_server.temperature())
        if temperature > 25:
            fan_status = True
        else:
            fan_status = False    
    
        if not inqueue.empty():
            query = inqueue.get()
            logger.info(f"query -> {query!r}")
            if query == "get":
                reply = "ON" if fan_status is True else "OFF"
                outqueue.put(reply)
            else:
                logger.info(f"out <- ?{str(query)}")
                outqueue.put(f"?{str(query)}")


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.CRITICAL)
		
PROCESS = multiprocessing.Process(target=process, args=(send_queue, recv_queue))
PROCESS.start()

def terminate():
   LOGGER.critical("TERMINATE FAN PROCESS")    
   PROCESS.terminate()
   

atexit.register(terminate)

class TheDBUSService(object):
   """
      <node>
         <interface name='net.ak.pydbus.fanserver'>
            <method name='identity'>
               <arg type='s' name='response' direction='out'/>
            </method>
            <method name='get'>
               <arg type='s' name='response' direction='out'/>
            </method>
            <method name='quit'/>
         </interface>
      </node>
	"""
   def quit(self):
     """removes this object from the DBUS connection and exits"""
     loop.quit()
   
   def identity(self):
       return IDENTITY
   
   def get(self):
      return self._communicate("get")
   
   def _communicate(self, command):
      global PROCESS
      send_queue.put(command)
      return recv_queue.get()
	

bus = SessionBus()
bus.publish("net.ak.pydbus.fanserver", TheDBUSService())
loop.run()
