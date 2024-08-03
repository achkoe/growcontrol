#!/usr/bin/env python

import xmlrpc.client
import settings

ht_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{settings.ht_server_port}")
fan_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{settings.fan_server_port}")

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
     reply = fan_proxy.get()
   elif command == "t":
     reply = ht_proxy.temperature()
   elif command == "h":
     reply = ht_proxy.humidity()
   elif command == "s":
      arg = input("set temperature to:")
      reply = ht_proxy.settemperature(float(arg))
   print(reply)

