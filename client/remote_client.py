#!/usr/bin/env python
import argparse
import xmlrpc.client
import configuration

sensors_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.sensors_server_port}")
fan_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.fan_server_port}")
light_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.light_server_port}")

choice_t = ["t", "T", "temperature"]
choice_h = ["h", "H", "humidity"]
choice_w = ["w", "W", "waterlevel"]
choice_m = ["m", "M", "moisture"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("what", 
                        choices=choice_t + choice_h + choice_m + choice_w,
                        help="set what")
    parser.add_argument("value", type=float, help="value")
    parser.add_argument("-c", "--channel", type=int, help="moisture channel", default=0)
    args = parser.parse_args()
    if args.what in choice_t:
        sensors_proxy.settemperature(args.value)
    elif args.what in choice_h:
        sensors_proxy.sethumidity(args.value)
    if args.what in choice_w:
        sensors_proxy.setwaterlevel(args.value)
    if args.what in choice_m:
        sensors_proxy.setmoisture(args.channel, args.value)
        

def old():    
    help = """
    Valid commands:
    t, T - return temperature, set temperature
    h, H  - return humidity, set humidity
    m, M - return moisture, set moisture
    w, W _ return waterlevel, set waterlevel
    f - get fan status
    a - fan auto
    o - fan on
    l - get light status
    r - reload
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
        elif command == "T":
            arg = input("set temperature to:")
            reply = sensors_proxy.settemperature(float(arg))
        elif command == "H":
            arg = input("set humidity to:")
            reply = sensors_proxy.sethumidity(float(arg))
        elif command == "m":
            reply = sensors_proxy.moisture(0)
        elif command == "M":
            arg = input("set moisture to:")
            reply = sensors_proxy.setmoisture(int(arg))
        elif command == "w":
            reply = sensors_proxy.waterlevel()
        elif command == "W":
            arg = input("set waterlevel to:")
            reply = sensors_proxy.setwaterlevel(int(arg))
        elif command == "r":
            reply = sensors_proxy.reload()
            reply = fan_proxy.reload()
            reply = light_proxy.reload()

        print(reply)
