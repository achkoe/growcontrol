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

app = Flask(__name__)


@ app.route("/")
def index():
    return render_template('index.html', configuration=configuration, version=f"v{VERSION}")


@ app.route("/update")
def udpate():
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
        "humidity": humidity,
        "temperature": temperature,
        "fan": fan,
        "fan_mode": fan_mode,
        "light_mode": light_mode,
        "time": time.strftime("%X"),
        "pump": pump,
        "moisture": moisture,
        "waterlevel": waterlevel,
        "fanExhaustAir": fan_exhaust_air,
        "heater": heater,
        "heater_mode": heater_mode,
        "humidifier": humidifier,
        "humidifier_mode": humidifier_mode
    }
    reply.update(light)
    reply.update(settings)
    return reply


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
        return render_template('index.html', configuration=configuration, version=f"v{VERSION}")
    else:
        return render_template("settings.html", settings=load_settings(raw=True), version=f"v{VERSION}")


@ app.route("/toggleFan", methods=("POST", ))
def toggle_fan():
    print(request.get_json())
    # {'fan': 'Manual', 'fanOnOff': 'Off'}
    fan_mode = request.get_json()["fan_mode"]  # either 'Manual' or 'Auto'
    fan_state = request.get_json()["fanOnOff"]
    reply = fan_proxy.set_fan(fan_mode, fan_state)
    print(f"reply -> {reply}")
    return {"status": reply}


@ app.route("/toggleHeater", methods=("POST", ))
def toggle_heater():
    print("toggleHeater: ", request.get_json())
    # {'heater': 'Manual', 'heaterOnOff': 'Off'}
    heater_mode = request.get_json()["heater_mode"]  # either 'Manual' or 'Auto'
    heater_state = request.get_json()["heaterOnOff"]
    reply = fan_proxy.set_heater(heater_mode, heater_state)
    print(f"reply -> {reply}")
    return {"status": reply}


@ app.route("/toggleHumidifier", methods=("POST", ))
def toggle_humidifier():
    print("toggleHumidifier: ", request.get_json())
    # {'humidifier': 'Manual', 'humidifierOnOff': 'Off'}
    humidifier_mode = request.get_json()["humidifier_mode"]  # either 'Manual' or 'Auto'
    humidifier_state = request.get_json()["humidifierOnOff"]
    reply = fan_proxy.set_humidifier(humidifier_mode, humidifier_state)
    print(f"reply -> {reply}")
    return {"status": reply}


@ app.route("/toggleFanExhaustAir", methods=("POST", ))
def toggle_fan_exhaust_air():
    print(request.get_json())
    # {'fan': 'Manual', 'fanOnOff': 'Off'}
    fan_state = request.get_json()["fanExhaustAirOnOff"]
    reply = fan_proxy.set_fan_exhaust_air(fan_state)
    print(f"reply -> {reply}")
    return {"status": reply}


@ app.route("/toggleLight", methods=("POST", ))
def toggle_light():
    print(request.get_json())
    # 'light_mode': 'Manual', 'light_state': 'Off'}
    light_mode = request.get_json()["light_mode"]
    light_state = request.get_json()["lightOnOff"]
    reply = light_proxy.set(light_mode, light_state)
    return {"status": reply}


@ app.route("/togglePump1", methods=("POST", ))
@ app.route("/togglePump2", methods=("POST", ))
@ app.route("/togglePump3", methods=("POST", ))
def toggle_pump():
    index = int(request.full_path[-2])
    pump = request.get_json()
    pump_proxy = pump_proxies[index]
    reply = pump_proxy.set(pump[f"pump{index}OnOff"])
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
    try:
        with pathlib.Path(__file__).parent.parent.joinpath("watchdog.log").open("r") as fh:
            watchdog = fh.read()
    except Exception as watchdog:
        pass
    return render_template('watchdog.html', watchdog=watchdog, version=f"v{VERSION}")
