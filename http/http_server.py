# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
import logging
import pathlib
from flask import Flask, render_template, request
from icecream import ic
import configuration
from version import VERSION                                                                                                                                                                                                                                                         
from servers.base import load_settings, save_settings


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

sensors_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.sensors_server_port}")
fan_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.fan_server_port}")
light_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.light_server_port}")
pump_proxies = dict((key, xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.pump_moisture_dict[key]['pump']}")) for key in configuration.pump_moisture_dict)
logdata_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.logdata_server_port}")


settings = load_settings()
print(settings)

mode_dict = {
    'fan-mode': light_proxy.get_mode(),
    'heater-mode': light_proxy.get_mode(),
    'humidifier-mode': light_proxy.get_mode(),
    'light-mode': light_proxy.get_mode(),
}

onoff_dict = {
    'light-onoff': light_proxy.get(),
    'fan-onoff': fan_proxy.get_fan(),
    'exhaustfan-onoff': fan_proxy.get_fan_exhaust_air(),
    "heater-onoff": fan_proxy.get_heater(), 
    "humidifier-onoff": fan_proxy.get_humidifier(),
    "exhaustfan-onoff": fan_proxy.get_fan_exhaust_air(),
}

onoff_set_dict = {
    'light-onoff': light_proxy.set,
    'fan-onoff': fan_proxy.set_fan,
    'exhaustfan-onoff': fan_proxy.set_fan_exhaust_air,
    "heater-onoff": fan_proxy.set_heater, 
    "humidifier-onoff": fan_proxy.set_humidifier,
    "exhaustfan-onoff": fan_proxy.set_fan_exhaust_air,
}

for key in configuration.pump_moisture_dict.keys():
    onoff_dict[f"pump{key}-onoff"] = "OFF"
    onoff_set_dict[f"pump{key}-onoff"] = pump_proxies[key].set

app = Flask(__name__)


@ app.route("/")
def index():
    return render_template('index.html', 
                           configuration=configuration, 
                           version=f"v{VERSION}",
                           settings=load_settings(raw=True))


@ app.route("/status")
def status():
    humidity = sensors_proxy.humidity()
    temperature = sensors_proxy.temperature()
    waterlevel = sensors_proxy.waterlevel()
    humidifier = fan_proxy.get_humidifier()
    humidifier_mode = fan_proxy.get_humidifier_mode()
    fan = fan_proxy.get_fan()
    fan_mode = fan_proxy.get_fan_mode()
    heater = fan_proxy.get_heater()
    heater_mode = fan_proxy.get_heater_mode()
    fan_exhaust_air = fan_proxy.get_fan_exhaust_air()
    light = light_proxy.get()
    light_mode = light_proxy.get_mode()
    pump = dict((key, dict(on=pump_proxies[key].get(), state=pump_proxies[key].get_state())) for key in pump_proxies)
    moisture = dict((key, sensors_proxy.moisture(configuration.pump_moisture_dict[key]["channel"]))
                    for key in configuration.pump_moisture_dict)
    
    reply = {
        "value-humidity": humidity,
        "value-temperature": temperature,
        "value-time": time.strftime("%X"),
        "value-watersupplylevel": waterlevel,
        "value-fan": fan,
        "value-humidifier": humidifier,
        "value-heater": heater,
        "value-light": light,
        #
        "light-mode": light_mode,
        "fan-mode": fan_mode,
        "heater-mode": heater_mode,
        "humidifier-mode": humidifier_mode,
        #
        "exhaustfan-onoff": fan_exhaust_air,
        "light-onoff": light,
        "fan-onoff": fan, 
        "heater-onoff": heater, 
        "humidifier-onoff": humidifier
    }
    for key in configuration.pump_moisture_dict.keys():
        reply.update({f"pump{key}-onoff": pump[key]["on"]})
        reply.update({f"pump{key}-soilmoisture": moisture[key]})
    reply.update({"settings": settings})
    return reply


@ app.route("/control", methods=("POST", ))
def control():
    print(f"control -> {request.json}")
    the_id = request.json["id"]
    if the_id.endswith("mode"):
        mode = "Manual" if mode_dict[the_id] == "Auto" else "Auto"
        mode_dict[the_id] = mode
        {    
            'light-mode': light_proxy.set_mode,
            'fan-mode': fan_proxy.set_fan_mode,
            'heater-mode': fan_proxy.set_heater_mode,
            'humidifier-mode': fan_proxy.set_humidifier_mode
        }[the_id](mode)
    else:    # mode is onoff
        onoff = "OFF" if onoff_dict[the_id] == "ON" else "ON"
        print(onoff)
        onoff_dict[the_id] = onoff
        onoff_set_dict[the_id](onoff)
        
    return {"status": True}
    

@ app.route("/settings", methods=("POST", "GET"))
def editsettings():
    global settings
    if request.method == "POST":
        for key in request.form:
            settings[key] = request.form[key]
        settings = save_settings(settings)
        sensors_proxy.reload()
        fan_proxy.reload()
        light_proxy.reload()
        for key, pump_proxy in pump_proxies.items():
            pump_proxy.reload()
    return index()


@ app.route("/main", methods=("POST", "GET"))
def main():
    return {}


@ app.route("/toggleFan", methods=("POST", ))
def toggle_fan():
    print(request.get_json())
    # {'fan': 'Manual', 'fanOnOff': 'Off'}
    fan_mode = request.get_json()["fan_mode"]  # either 'Manual' or 'Auto'
    fan_state = request.get_json()["fanOnOff"]
    reply = fan_proxy.set_fan(fan_mode, fan_state)
    print(f"reply -> {reply}")
    return {"status": reply}


@app.route("/log", methods=("GET", ))
def log():
    return render_template('logdata.html', configuration=configuration, version=f"v{VERSION}")


@ app.route("/logdata")
def logdata():
    try:
        output_list, moisture_dict, min_max_mean = logdata_proxy.get()
        return dict(tth=output_list, m=moisture_dict, min_max_mean=min_max_mean)
    except Exception:
        print("logdata issue")
        return dict(tth=[], m={})
    

@app.route("/watchdog", methods=("GET", ))
def watchdog():
    status = "unknown"
    try:
        with pathlib.Path(__file__).parent.parent.joinpath("watchdog.log").open("r") as fh:
            status = fh.read()
    except Exception as watchdog:
        pass
    return {"watchdog": status}
