objControls = {};
objControls.fanExhaustAir = null;
objControls.cFan = null;
objControls.cHeater = null;
objControls.cLight = null;
objControls.cHumidifier = null;
objControls.oPump = {};

objStatus = {};
index_high = null;


function sendState(url, state) {
    console.log("sendState ", url, state);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(state),
    }).then(response => {
        if (!response.ok) {
            console.error('Error sending state to server');
        }
    }).catch(error => {
        console.error('Error sending state to server:', error);
    });
}

class Button {
    constructor(btnName) {
        this.btnName = btnName;
        this.updateStatusUrl = "/toggle" + btnName[0].toUpperCase() + btnName.slice(1);
        this.state = {};
        this.state[this.btnName + "OnOff"] = "Off";
        this.btnState = document.getElementById(btnName + "OnOffToggle")
        this.btnState.addEventListener("click", this.toggle_on_off.bind(this));
    }
    
    _toggle_on_off() {
        if (this.btnState.textContent == 'Off') {
            this.btnState.textContent = 'On';
            this.btnState.classList.remove('off');
            this.btnState.classList.add('on');
            this.state[this.btnName + "OnOff"] = "On";
        } else {
            this.btnState.textContent = 'Off';
            this.btnState.classList.remove('on');
            this.btnState.classList.add('off');
            this.state[this.btnName + "OnOff"] = "Off";
        }
    }
    toggle_on_off() {
        this._toggle_on_off();
        this.sendStatusToServer();
    }
    
    sendStatusToServer() {
        sendState(this.updateStatusUrl, this.state);
    }
    
    updateFromServer(data) {
        // console.log("updateFromServer ", this.btnName, data[this.btnName]);
        this.btnState.textContent = data[this.btnName] == "ON" ? "Off" : "On";  // think reverse because we are calling _toggle_on_off
        this._toggle_on_off();
    }
}

class ConnectedButton extends Button {
    constructor(btnName) {
        super(btnName);
        this.btnControl = document.getElementById(btnName + "_mode");
        this.state[this.btnName + "_mode"] = "Auto";
        this.btnControl.addEventListener("click", this.toggle_auto_manual.bind(this));
    }
    
    _toggle_auto_manual() {
        if (this.btnControl.textContent === 'Auto' ) {
            this.btnControl.textContent = 'Manual';
            this.btnControl.classList.remove('auto');
            this.btnControl.classList.add('manual');
            this.btnState.disabled = false;
            this.state[this.btnName + "_mode"] = "Manual";
        } else {
            this.btnControl.textContent = 'Auto' ;
            this.btnControl.classList.remove('manual');
            this.btnControl.classList.add('auto');
            this.btnState.disabled = true;
            this.state[this.btnName + "_mode"] = "Auto";
        }
    }
    
    toggle_auto_manual() {
        this._toggle_auto_manual();
        this.sendStatusToServer();
    }
    
    updateFromServer(data) {
        if (this.btnName == "humidifier") {
            console.error("NOT IMPLEMENTED");
            return;
        }
        //console.log("updateFromServer ", this.btnName, data[this.btnName]);
        this.btnState.textContent = data[this.btnName] == "ON" ? "Off" : "On";  // think reverse because we are calling _toggle_on_off
        this._toggle_on_off();
        this.btnControl.textContent = data[this.btnName + "_mode"] == "Auto" ? "Manual" : "Auto";
        this._toggle_auto_manual();
        objStatus[this.btnName].innerText = data[this.btnName] == "ON" ? "On" : "Off";
    }
}


class PumpButton extends Button {
    updateFromServer(data) {
        let index = this.btnName.substr(-1);
        console.log("updateFromServer ", this.btnName, data["pump"][index]["on"]);
        this.btnState.textContent = data["pump"][index]["on"] == "ON" ? "Off" : "On";  // think reverse because we are calling _toggle_on_off
        this._toggle_on_off();
    }
}


document.addEventListener("DOMContentLoaded", function() {
    
    objControls.fanExhaustAir = new Button("fanExhaustAir");
    objControls.cFan = new ConnectedButton("fan"); 
    objControls.cHeater = new ConnectedButton("heater"); 
    objControls.cLight = new ConnectedButton("light");
    objControls.cHumidifier = new ConnectedButton("humidifier")

    for (let index = 1; index < 10; index++) {
        var pumpToggle = document.getElementById("boxpump_" + index);
        if (pumpToggle == null) break;
        index_high = index;
        objControls.oPump[index] = new PumpButton("pump" + index);
        objStatus["boxmoisture_" + index] = document.getElementById("boxmoisture_" + index)
        objStatus["boxpump_" + index] = document.getElementById("pump_" + index);
        objStatus["pump" + index] = document.getElementById("pump_" + index)
        objStatus["moisture_" + index] = document.getElementById("moisture_" + index)
    }
    
    ["humidity", "temperature", "waterlevel", "boxwaterlevel", "boxtemperature", "boxhumidity", "time", "fan", "heater", "light"].forEach(function(field) {
        objStatus[field] = document.getElementById(field);
    });
    // console.log(objStatus);
    receiceStatusFromServer();

});


function receiceStatusFromServer() {
    const urlUpdate = `/update`;

    function makeHttpRequest() {
        fetch(urlUpdate)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();  // Change to response.json() if expecting JSON
            })
            .then(data => {
                //console.log('data:', data);
                // update status
                objStatus.temperature.innerText = data["temperature"].toFixed(1);
                objStatus.humidity.innerText = data["humidity"].toFixed(1);
                objStatus.time.innerText = data["time"];

                if (data["waterlevel"] == 0) {
                    objStatus.waterlevel.innerText = "CRITICAL";
                } else if (data["waterlevel"] == 1) {
                    objStatus.waterlevel.innerText = "LOW";
                } else if (data["waterlevel"] == 2) {
                    objStatus.waterlevel.innerText = "MEDIUM";
                } else if (data["waterlevel"] == 3) {
                    objStatus.waterlevel.innerText = "FULL";
                }

                objStatus.boxwaterlevel.classList.remove("alert");
                objStatus.boxwaterlevel.classList.remove("warn");
                if (data.waterlevel == 0) {
                    objStatus.boxwaterlevel.classList.add("alert");
                } else if (data.waterlevel == 1) {
                    objStatus.boxwaterlevel.classList.add("warn");
                } 

                if ((data.temperature > data.temperature_high_critical_level) | (data.temperature < data.temperature_low_critical_level)){
                    objStatus.boxtemperature.classList.add("alert");
                } else {
                    objStatus.boxtemperature.classList.remove("alert");
                }

                if ((data.humidity > data.humidity_high_critical_level) | (data.humidity < data.humidity_low_critical_level)){
                    objStatus.boxhumidity.classList.add("alert");
                } else {
                    objStatus.boxhumidity.classList.remove("alert");
                }

                for (let index = 1; index <= index_high; index++) {
                    objStatus["moisture_" + index].innerText = data["moisture"][index].toFixed(1);
                    if (data["moisture"][index] <= data["moisture_low_level"]) {
                        objStatus["boxmoisture_" + index].classList.add("alert");
                    } else {
                        objStatus["boxmoisture_" + index].classList.remove("alert");
                    }
                }

                // update controls
                for (const [key, value] of Object.entries(objControls)) {
                    if (key == "humidifier") {
                        console.error("NOT IMPLEMENTED");
                        continue;
                    }
                    if (key == "oPump") {
                        for (const [key_, value_] of Object.entries(value)) {
                            objStatus["boxpump_" + key_].innerText = data["pump"][key_]["state"];
                            // console.log(data);
                            value_.updateFromServer(data);
                        }
                    } else {
                        value.updateFromServer(data);
                    }
                }            
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    }

    // Call the function immediately
    makeHttpRequest();

    // Set the interval to call the function every 2 seconds (2000 milliseconds)
    setInterval(makeHttpRequest, 2000);

}