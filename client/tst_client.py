#!/usr/bin/env python

# Based on http://stackoverflow.com/questions/22390064/use-dbus-to-just-send-a-message-in-python

# Python script to call the methods of the DBUS Test Server

from pydbus import SessionBus

#get the session bus
bus = SessionBus()
#get the object
ht_server = bus.get("net.ak.pydbus.htserver")
fan_server = bus.get("net.ak.pydbus.fanserver")

help = """
Valid commands:
t - return temperature
h  - return humidity
f - get fan status
s <value> - set temperature
"""
print(help)

while True:
   command = input("Command: ")
   if command == "q":
      break
   elif command == "f":
     reply = fan_server.get()
   elif command == "t":
     reply = ht_server.temperature()
   elif command == "h":
     reply = ht_server.humidity()
   elif command == "s":
      arg = input("set temperature to:")
      reply = ht_server.settemperature(float(arg))
   print(reply)

fan_server.quit()
ht_server.quit()