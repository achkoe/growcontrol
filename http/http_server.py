# flask --app http_server run --debug --host 0.0.0.0

import xmlrpc.client
import time
import json
import logging
import pathlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from icecream import ic
from oncalendar import BaseIterator
from version import VERSION                                                                                                                                                                                                                                                         
from servers.base import load_settings, save_settings
import configuration


logging.getLogger('werkzeug').setLevel(logging.ERROR)

sensors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")
actors_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.actors_server_port}")
logdata_proxy = xmlrpc.client.ServerProxy(f"http://localhost:{configuration.logdata_server_port}")

app = Flask(__name__)
app._settings = load_settings()
hint = dict(pumps=list(configuration.pump_dict.keys()), moistures=list(configuration.moisture_dict.keys()))

@ app.route("/")
def index():
    hint.update({"timetitle": dict()})
    for key, value in app._settings.items():
        if value["type"] == "time":
            hint["timetitle"][key] = dict(ontime="Use e.g. *:00:01 or 17:50", offtime="Use e.g. *:00:01 or 17:50")
            for subkey in hint["timetitle"][key]:
                try:
                    it = BaseIterator(app._settings[key][subkey]["value"], datetime.now())
                    title = "\n".join(next(it).isoformat() for _ in range(10))
                    hint["timetitle"][key][subkey] = title
                except Exception as e:
                    print(e)
                                    
    return render_template('index.html', 
                           version=f"v{VERSION}",
                           configuration=configuration,
                           hint=hint,
                           settings=app._settings)


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
        data["stime"] = time.time()
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
    

@app.route("/settings", methods=("POST", "GET"))
def settings():
    if request.method == "POST":
        for key in request.form:
            print(f"{key}: {request.form[key]}")
            if key.endswith("time"):
                try:
                    next(BaseIterator(request.form[key], datetime.now()))
                    key_a, key_b = key.split("-")
                    app._settings[key_a][key_b]["value"] = request.form[key]
                except Exception as e:
                    print(e)                    
                    continue
            else:
                app._settings[key]["value"] = request.form[key].strip()
    save_settings(app._settings)
    sensors_proxy.reload()
    actors_proxy.reload()
        # pump_proxy.reload()
    return redirect(url_for("index"))


@app.route("/verifytimeinput", methods=("POST",))
def verifytimeinput():
    data = request.get_json()
    value = data["value"]
    try:
        it = BaseIterator(value, datetime.now())
        title = "\n".join(next(it).isoformat() for _ in range(10))
        valid = True
    except Exception:
        title = "Use e.g. *:00:01 or 17:50"
        valid = False
    return {"valid": valid, "title": title}


@ app.route("/logdata")
def logdata():
    try:
        q = logdata_proxy.get()
        q.update(dict(status="ok"))
        ic(q)
        return q
    except Exception as e:
        print(f"logdata issue -> {e}")
        return dict(status="error")
    

@app.route("/watchdog", methods=("GET", ))
def watchdog():
    status = "unknown"
    try:
        with pathlib.Path(__file__).parent.parent.joinpath("watchdog.log").open("r") as fh:
            status = fh.read()
    except Exception as watchdog:
        pass
    return {"watchdog": status}
