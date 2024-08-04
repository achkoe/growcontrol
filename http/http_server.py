# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
from flask import Flask, render_template, request
import configuration
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
fan_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.fan_server_port}")
light_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.light_server_port}")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/update")
def udpate():
    humidity = sensors_proxy.humidity()
    temperature = sensors_proxy.temperature()
    fan  = fan_proxy.get()
    light = light_proxy.get()
    reply = {
        "humidity": humidity,
        "temperature": temperature,
        "fan": fan,
        "time": time.strftime("%X")
    }
    reply.update(light)
    return reply


@app.route("/toggleFan", methods=("POST", ))
def toggle_fan():
    print(request.get_json())
    # {'fan': 'Manual', 'fanOnOff': 'Off'}
    fan_mode = request.get_json()["fan"]  # either 'Manual' or 'Auto'
    fan_state = request.get_json()["fanOnOff"]
    if fan_mode == "Manual":
        reply = fan_proxy.manual()
    else:
        reply = fan_proxy.auto()
    print(f"reply -> {reply}")
    if fan_state == "On":
        reply = fan_proxy.fanon()
    else:
        reply = fan_proxy.fanoff()
    print(f"reply -> {reply}")
    return {"status": "OK"}


@app.route("/toggleLight", methods=("POST", ))
def toggle_light():
    print(request.get_json())
    # 'light': 'Manual', 'light1': 'Off', 'light2': 'Off'}
    light_mode = request.get_json()["light"]
    light_1_state = request.get_json()["light1"]
    light_2_state = request.get_json()["light2"]
    reply = light_proxy.set(light_mode, light_1_state, light_2_state)
    return {"status": reply}
    
    
    if light_mode == "Manual":
        reply = light_proxy.manual()
    else:
        reply = light_proxy.auto()
    print(f"reply -> {reply}")
    
    if light_1_state == "On":
        reply = light_proxy.light1on()
    else:
        reply = light_proxy.light1off()
    print(f"reply -> {reply}")
    
    if light_2_state == "On":
        reply = light_proxy.light2on()
    else:
        reply = light_proxy.light2off()
    print(f"reply -> {reply}")

    return {"status": "OK"}
