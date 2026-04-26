# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
import json
import logging
import pathlib
from flask import Flask, render_template, request, redirect, url_for, jsonify
from icecream import ic
from version import VERSION                                                                                                                                                                                                                                                         
from servers.base import load_settings, save_settings
import configuration


logging.getLogger('werkzeug').setLevel(logging.ERROR)

sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
actors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.actors_server_port}")

app = Flask(__name__)
app._settings = load_settings()
hint = dict(pumps=list(configuration.pump_dict.keys()), moistures=list(configuration.moisture_dict.keys()))

@ app.route("/")
def index():
    return render_template('index.html', 
                           version=f"v{VERSION}",
                           configuration=configuration,
                           hint=hint,
                           settings=load_settings(raw=True))


@ app.route("/status")
def status():
    
    data = {
        "temperature": '?',
        "humidity": '?',
        "moisture": ['?'] * len(hint["moistures"]),
        "moisture-status": ['?'] * len(hint["moistures"]),
        "waterlevel": "?",
        "sensorstatus": "?",
        "actorstatus": "?"
    }
    
    try:
        data["time"] = time.strftime("%X")
        data.update(sensors_proxy.get())
        
        for key in ["temperature", "humidity"]:
            if data[key] < float(app._settings[f"{key}_low_level"]["value"]):
                data[f"{key}-status"] = "below"
            elif data[key] > float(app._settings[f"{key}_high_level"]["value"]):
                data[f"{key}-status"] = "above"
            else:
                data[f"{key}-status"] = "okay"
        data["moisture-status"] = []
        for value in data["moisture"]:
            if value > float(app._settings["moisture_high_level"]["value"]):
                data["moisture-status"].append("above")
            elif value < float(app._settings["moisture_low_level"]["value"]):
                data["moisture-status"].append("below")
            else:
                data["moisture-status"].append("okay")
                
        print("HERE", data)
        data["sensorstatus"] = "ok"
    except Exception as e:
        print(e)
        data["sensorstatus"] = repr(e)
        
    try:
        data.update(actors_proxy.get())
        data["actorstatus"] = "ok"
    except Exception as e:
        print(e)
        data["actorstatus"] = repr(e)
        
    #print(json.dumps(data, indent=4))
    return data



@app.route("/buttonclick", methods=("POST", ))
def buttonclick():
    recv = request.json
    print(f"buttonclick -> {recv}")
    _, what, element = recv["id"].split("-")
    classlist = recv["classlist"].split(" ")
    # print(f"what={what}, element={element}, classlist={classlist}")
    actors_proxy.set(element, what)    
    return {}
    


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
