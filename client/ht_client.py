#!/usr/bin/env python

# Based on http://stackoverflow.com/questions/22390064/use-dbus-to-just-send-a-message-in-python
# Python script to call the methods of the DBUS ht server

import xmlrpc.client

if __name__ == "__main__":
   proxy = xmlrpc.client.ServerProxy('http://localhost:4000')

   # Print list of available methods
   print(proxy.system.listMethods())

   print(proxy.temperature())


