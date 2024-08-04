#!/usr/bin/env python

import xmlrpc.client
import configuration

sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
fan_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.fan_server_port}")
light_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.light_server_port}")

help = """
Valid commands:
t - return temperature
h  - return humidity
f - get fan status
l - get light status
s <value> - set temperature
a - fan auto
o - fan on
"""
print(help)

while True:
   command = input("Command: ")
   if command == "q":
      break
   elif command == "f":
     reply = fan_proxy.get()
   elif command == "a":
     reply = fan_proxy.auto()
   elif command == "o":
     reply = fan_proxy.on()
   elif command == "l":
     reply = light_proxy.get()
   elif command == "t":
     reply = sensors_proxy.temperature()
   elif command == "h":
     reply = sensors_proxy.humidity()
   elif command == "s":
      arg = input("set temperature to:")
      reply = sensors_proxy.settemperature(float(arg))
   print(reply)

