#!/usr/bin/env python
"""Server to deliver temperature and humidity over dbus."""

# Based on http://stackoverflow.com/questions/22390064/use-dbus-to-just-send-a-message-in-python


from gi.repository import GLib
from pydbus import SessionBus
import multiprocessing
import time

IDENTITY = "ht_server.py v0.0.1"
loop = GLib.MainLoop()
send_queue = multiprocessing.Queue()
recv_queue = multiprocessing.Queue()



def process(inqueue: multiprocessing.Queue, outqueue: multiprocessing.Queue) -> None:
    # So far just for testing
    print("PROCESS STARTED")
    temperature = 24.23456
    humidity = 48.1
    while True:
        time.sleep(0.01)
        if not inqueue.empty():
            query = inqueue.get()
            print(f"query -> {query!r}")
            if query == "temperature":
                print(f"out <- {temperature}")
                outqueue.put(temperature)
            elif query == "humidity":
                print(f"out <- {humidity}")
                outqueue.put(humidity)
            else:
                print(f"out <- ?{str(query)}")
                outqueue.put(f"?{str(query)}")

		
PROCESS = multiprocessing.Process(target=process, args=(send_queue, recv_queue))
PROCESS.start()


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
         </interface>
      </node>
	"""
   def quit(self):
     """removes this object from the DBUS connection and exits"""
     loop.quit()

   def identity(self):
       return IDENTITY
   
   def temperature(self):
      return "{:4.1f}".format(self._communicate("temperature"))       

   def humidity(self):
      return "{:4.1f}".format(self._communicate("humidity")       )
   
   def _communicate(self, command):
      global PROCESS
      send_queue.put(command)
      return recv_queue.get()
	

bus = SessionBus()
bus.publish("net.ak.pydbus.htserver", TheDBUSService())
loop.run()
