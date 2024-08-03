# flask --app http_server run --debug --host 0.0.0.0

from flask import Flask, render_template
from pydbus import SessionBus



app = Flask(__name__)

# get the session bus
bus = SessionBus()
#get the object
ht_server = bus.get("net.ak.pydbus.htserver")
fan_server = bus.get("net.ak.pydbus.fanserver")

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/update")
def udate():
    humidity = ht_server.humidity()
    temperature = ht_server.temperature()
    fan  = fan_server.get()
    return {
        "humidity": humidity,
        "temperature": temperature,
        "fan": fan
    }



