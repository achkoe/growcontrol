#!/usr/bin/env python

# Based on http://stackoverflow.com/questions/22390064/use-dbus-to-just-send-a-message-in-python
# Python script to call the methods of the DBUS ht server

from pydbus import SessionBus


if __name__ == "__main__":
   # get the session bus
   bus = SessionBus()
   #get the object
   ht_server = bus.get("net.ak.pydbus.htserver")

   print("Commands: 'identity' or 'humidity' or 'temperature' or 'quit'")
   while True:
      command = input("Command: ")
      print(f"{command!r}")
      if command == "quit":
         break
      elif command in ["humidity"]:
         reply = ht_server.humidity()
      elif command == "temperature":
         reply = ht_server.temperature()
      elif command == "identity":
         reply = ht_server.identity()
      else:
         print(f"Invalid command: {command!r}")
         continue
      print(reply)

ht_server.quit()