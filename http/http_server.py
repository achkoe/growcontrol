# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
import json
import logging
import pathlib
from flask import Flask, render_template, request, redirect, url_for
from icecream import ic
from version import VERSION                                                                                                                                                                                                                                                         
from servers.base import load_settings, save_settings


logging.getLogger('werkzeug').setLevel(logging.ERROR)


app = Flask(__name__)
configuration = dict(moisture_dict=dict())

@ app.route("/")
def index():
    return render_template('index.html', 
                           version=f"v{VERSION}",
                           configuration=configuration,
                           settings=load_settings(raw=True))


@ app.route("/status")
def status():
    with pathlib.Path(__file__).parent.joinpath("_data.json").open("r") as fh:
        data = json.load(fh)
    reply = data
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
            'pump-mode': pump_proxy.set_mode,
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
        pump_proxy.reload()
    return redirect(url_for("index"))


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
