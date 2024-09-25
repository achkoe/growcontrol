# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
from flask import Flask, render_template, request
from icecream import ic
import configuration
import logging
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
    return render_template('index.html', configuration=configuration)


@ app.route("/update")
def udpate():
    humidity = sensors_proxy.humidity()
    temperature = sensors_proxy.temperature()
    waterlevel = sensors_proxy.waterlevel()
    fan = fan_proxy.get()
    light = light_proxy.get()
    pump = dict((key, pump_proxies[key].get()) for key in pump_proxies)
    moisture = dict((key, sensors_proxy.moisture(configuration.pump_moisture_dict[key]["channel"]))
                    for key in configuration.pump_moisture_dict)
    reply = {
        "humidity": humidity,
        "temperature": temperature,
        "fan": fan,
        "time": time.strftime("%X"),
        "pump": pump,
        "moisture": moisture,
        "waterlevel": waterlevel
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
    return render_template("settings.html", settings=load_settings(raw=True))


@ app.route("/toggleFan", methods=("POST", ))
def toggle_fan():
    print(request.get_json())
    # {'fan': 'Manual', 'fanOnOff': 'Off'}
    fan_mode = request.get_json()["fan"]  # either 'Manual' or 'Auto'
    fan_state = request.get_json()["fanOnOff"]
    reply = fan_proxy.set(fan_mode, fan_state)
    print(f"reply -> {reply}")
    return {"status": reply}


@ app.route("/toggleLight", methods=("POST", ))
def toggle_light():
    print(request.get_json())
    # 'light': 'Manual', 'light1': 'Off', 'light2': 'Off'}
    light_mode = request.get_json()["light"]
    light_1_state = request.get_json()["light1"]
    light_2_state = request.get_json()["light2"]
    reply = light_proxy.set(light_mode, light_1_state, light_2_state)
    return {"status": reply}


@ app.route("/togglePump", methods=("POST", ))
def toggle_pump():
    pump = request.get_json()
    print(pump)
    pump_proxy = pump_proxies[int(pump["index"])]
    reply = pump_proxy.set(pump["mode"], pump["pumpOnOff"])
    return {"status": reply}


@app.route("/log", methods=("GET", ))
def log():
    return render_template('logdata.html')


@app.route("/logdata")
def logdata():
    time_temperature_humidity_list, moisture_dict = logdata_proxy.get()
    # for item in time_temperature_humidity_list:
    #     item[0] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[0]))
    # ic(time_temperature_humidity_list)
    # for key, value in moisture_dict.items():
    #     for item in value:
    #         item[0] = time.strftime(
    #             '%Y-%m-%d %H:%M:%S', time.localtime(item[0]))
    # ic(moisture_dict)
    # ic(time_temperature_humidity_list)
    return dict(tth=time_temperature_humidity_list, m=moisture_dict)
