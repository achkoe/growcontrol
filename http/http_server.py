# flask --app http_server run --debug --host 0.0.0.0

from flask import Flask, render_template
import xmlrpc.client
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
        "fan": fan
    }
    reply.update(light)
    return reply



