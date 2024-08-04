# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
from flask import Flask, render_template, request
import configuration

sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
fan_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.fan_server_port}")
light_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.light_server_port}")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/update")
def udate():
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


@app.route("/toggle", methods=("POST", ))
def toggle_fan():
    fan_mode = request.get_json()["toggleState"]  # True means 'Manual', False means 'Auto'
    fan_state = request.get_json()["isOn"]
    print(f"fan_mode -> {fan_mode}, fan_state -> {fan_state}")
    if fan_mode is True:
        reply = fan_proxy.manual()
    else:
        reply = fan_proxy.auto()
    print(f"reply -> {reply}")
    if fan_state is True:
        reply = fan_proxy.fanon()
    else:
        reply = fan_proxy.fanoff()
    print(f"reply -> {reply}")

    return {"status": "OK"}    

