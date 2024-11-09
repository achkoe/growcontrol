
function callServerEveryTwoSeconds() {
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
                // console.log('Success:', data);
                // console.log('data:', data);
                console.log('heater: ' + data["heater"] + ', heater_mode: ' + data["heater_mode"]);
                var e;
                // show the current data for fields
                ["fan", "fan_mode", "light_state", "time", "light_mode", "heater", "heater_mode"].forEach(function(field) {
                    e = document.getElementById(field);
                    e.innerText = data[field];
                });
                
                [["fan_mode", ["fanOnOffToggle"]], ["heater_mode", ["heaterOnOffToggle"]], ["light_mode", ["lightToggle"]]].forEach(function(fields) {
                    e = document.getElementById(fields[0]);
                    if (data[fields[0]] == "Manual") {
                        e.classList.remove('auto');
                        e.classList.add('manual');
                        fields[1].forEach(function(field) {
                            e = document.getElementById(field);
                            e.disabled = false;
                        });
                    } else {
                        e.classList.remove('manual');
                        e.classList.add('auto');
                        fields[1].forEach(function(field) {
                            e = document.getElementById(field);
                            e.disabled = true;
                        });
                    }
                });
                
                [["fanOnOffToggle", "fan"], ["heaterOnOffToggle", "heater"], ["lightToggle", "light_state"], ["fanExhaustAirOnOff", "fan_exhaust_air"]].forEach(function(fields) {
                    e = document.getElementById(fields[0]);
                    if (data[fields[1]] == "ON") {
                        e.textContent = 'On';
                        e.classList.remove('off');
                        e.classList.add('on');
                    } else {
                        e.textContent = 'Off';
                        e.classList.remove('on');
                        e.classList.add('off');
                    }
                });    

                ["humidity", "temperature"].forEach(function(field) {
                    e = document.getElementById(field);
                    e.innerText = data[field].toFixed(1);
                });

                e = document.getElementById("waterlevel");
                if (data["waterlevel"] == 0) {
                    e.innerText = "CRITICAL";
                } else if (data["waterlevel"] == 1) {
                    e.innerText = "LOW";
                } else if (data["waterlevel"] == 2) {
                    e.innerText = "MEDIUM";
                } else if (data["waterlevel"] == 3) {
                    e.innerText = "FULL";
                }
                e = document.getElementById("boxwaterlevel");
                e.classList.remove("alert");
                e.classList.remove("warn");
                if (data.waterlevel == 0) {
                    e.classList.add("alert");
                } else if (data.waterlevel == 1) {
                    e.classList.add("warn");
                } 

                e = document.getElementById("boxtemperature");
                if ((data.temperature > data.temperature_high_critical_level) | (data.temperature < data.temperature_low_critical_level)){
                    e.classList.add("alert");
                    console.log("alert");
                } else {
                    e.classList.remove("alert");
                }
                e = document.getElementById("boxhumidity");
                if ((data.humidity > data.humidity_high_critical_level) | (data.humidity < data.humidity_low_critical_level)){
                    e.classList.add("alert");
                    console.log("alert");
                } else {
                    e.classList.remove("alert");
                }
                for (index = 1; index < 10; index++) {
                    e = document.getElementById("pump_" + index);
                    if (e === null) break;
                    e.innerText = data["pump"][index]["state"] + "\n(" + data["pump"][index]["on"] + ")";
                    e = document.getElementById("moisture_" + index);
                    e.innerText = data["moisture"][index].toFixed(1);
                    e = document.getElementById("boxpump_" + index)
                    if (data["moisture"][index] <= data["moisture_low_level"]) {
                        e.classList.add("alert");
                    } else {
                        e.classList.remove("alert");
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

// Start the process
callServerEveryTwoSeconds();


document.addEventListener("DOMContentLoaded", function() {
    const fan_mode = document.getElementById('fan_mode');
    const fanOnOffToggle = document.getElementById('fanOnOffToggle');
    const heater_mode = document.getElementById('heater_mode');
    const heaterOnOffToggle = document.getElementById('heaterOnOffToggle');
    const fanExhaustAirOnOffToggle = document.getElementById('fanExhaustAirOnOff');
    const light_mode = document.getElementById('light_mode');
    const lightToggle = document.getElementById('lightToggle');

    
    function sendState(url, state) {
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
    
    function updateFanState() {
        const state = {
            fan: fan_mode.textContent === 'Manual' ? 'Manual' : 'Auto',
            fanOnOff: fanOnOffToggle.textContent === 'On' ? 'On' : 'Off'
        };
        sendState('/toggleFan', state);
    }

    function updateHeaterState() {
        const state = {
            heater: heater_mode.textContent === 'Manual' ? 'Manual' : 'Auto',
            heaterOnOff: heaterOnOffToggle.textContent === 'On' ? 'On' : 'Off'
        };
        sendState('/toggleHeater', state);
    }

    function updateFanExhaustAirState() {
        const state = {
            fanExhaustAirOnOff: fanExhaustAirOnOffToggle.textContent === 'On' ? 'On' : 'Off'
        };
        sendState('/toggleFanExhaustAir', state);
    }

    function updateLightState() {
        const state = {
            light_mode: light_mode.textContent === 'Manual' ? 'Manual' : 'Auto',
            light_state: lightToggle.textContent === 'On' ? 'On' : 'Off',
        };
        sendState('/toggleLight', state);
    }

    fan_mode.addEventListener('click', function() {
        if (fan_mode.textContent === 'Auto') {
            fan_mode.textContent = 'Manual';
            fan_mode.classList.remove('auto');
            fan_mode.classList.add('manual');
            fanOnOffToggle.disabled = false;
        } else {
            fan_mode.textContent = 'Auto';
            fan_mode.classList.remove('manual');
            fan_mode.classList.add('auto');
            fanOnOffToggle.disabled = true;
            fanOnOffToggle.textContent = 'Off';  // Reset the Fan On/Off button to Off
            fanOnOffToggle.classList.remove('on');
            fanOnOffToggle.classList.add('off');
        }
        updateFanState();
    });

    fanOnOffToggle.addEventListener('click', function() {
        if (fanOnOffToggle.textContent === 'Off') {
            fanOnOffToggle.textContent = 'On';
            fanOnOffToggle.classList.remove('off');
            fanOnOffToggle.classList.add('on');
        } else {
            fanOnOffToggle.textContent = 'Off';
            fanOnOffToggle.classList.remove('on');
            fanOnOffToggle.classList.add('off');
        }
        updateFanState();
    });

    heater_mode.addEventListener('click', function() {
        if (heater_mode.textContent === 'Auto') {
            heater_mode.textContent = 'Manual';
            heater_mode.classList.remove('auto');
            heater_mode.classList.add('manual');
            heaterOnOffToggle.disabled = false;
        } else {
            heater_mode.textContent = 'Auto';
            heater_mode.classList.remove('manual');
            heater_mode.classList.add('auto');
            heaterOnOffToggle.disabled = true;
            heaterOnOffToggle.textContent = 'Off';  // Reset the heater On/Off button to Off
            heaterOnOffToggle.classList.remove('on');
            heaterOnOffToggle.classList.add('off');
        }
        updateHeaterState();
    });

    heaterOnOffToggle.addEventListener('click', function() {
        if (heaterOnOffToggle.textContent === 'Off') {
            heaterOnOffToggle.textContent = 'On';
            heaterOnOffToggle.classList.remove('off');
            heaterOnOffToggle.classList.add('on');
        } else {
            heaterOnOffToggle.textContent = 'Off';
            heaterOnOffToggle.classList.remove('on');
            heaterOnOffToggle.classList.add('off');
        }
        updateHeaterState();
    });

    fanExhaustAirOnOffToggle.addEventListener('click', function() {
        if (fanExhaustAirOnOffToggle.textContent === 'Off') {
            fanExhaustAirOnOffToggle.textContent = 'On';
            fanExhaustAirOnOffToggle.classList.remove('off');
            fanExhaustAirOnOffToggle.classList.add('on');
        } else {
            fanExhaustAirOnOffToggle.textContent = 'Off';
            fanExhaustAirOnOffToggle.classList.remove('on');
            fanExhaustAirOnOffToggle.classList.add('off');
        }
        updateFanExhaustAirState();
    });

    light_mode.addEventListener('click', function() {
        if (light_mode.textContent === 'Auto') {
            light_mode.textContent = 'Manual';
            light_mode.classList.remove('auto');
            light_mode.classList.add('manual');
            lightToggle.disabled = false;
        } else {
            light_mode.textContent = 'Auto';
            light_mode.classList.remove('manual');
            light_mode.classList.add('auto');
            lightToggle.disabled = true;
            lightToggle.textContent = 'Off';  // Reset the Light button to Off
            lightToggle.classList.remove('on');
            lightToggle.classList.add('off');
        }
        updateLightState();
    });

    lightToggle.addEventListener('click', function() {
        if (lightToggle.textContent === 'Off') {
            lightToggle.textContent = 'On';
            lightToggle.classList.remove('off');
            lightToggle.classList.add('on');
        } else {
            lightToggle.textContent = 'Off';
            lightToggle.classList.remove('on');
            lightToggle.classList.add('off');
        }
        updateLightState();
    });
    
    function updatePumpState(id) {
        console.log(id);
        index = id.split("_").pop();
        const pumpToggle = document.getElementById("pumpToggle_" + index);
        const pumpOnOffToggle = document.getElementById("pumpOnOffToggle_" + index);
        const state = {
            index: index,
            mode: pumpToggle.textContent === 'Manual' ? 'Manual' : 'Auto',
            pumpOnOff: pumpOnOffToggle.textContent === 'On' ? 'On' : 'Off'
        };
        // console.log(state);
        sendState('/togglePump', state);
    }

    var pumpToggle;
    for (index=1; index < 10; index++) {
        pumpToggle = document.getElementById("pumpToggle_" + index);
        if (pumpToggle == null) break;
        
        pumpToggle.addEventListener('click', function() {
            var index = this.id.split("_").pop();
            const pumpOnOffToggle = document.getElementById("pumpOnOffToggle_" + index);
            if (this.textContent === 'Auto') {
                this.textContent = 'Manual';
                this.classList.remove('auto');
                this.classList.add('manual');
                pumpOnOffToggle.disabled = false;
            } else {
                this.textContent = 'Auto';
                this.classList.remove('manual');
                this.classList.add('auto');
                pumpOnOffToggle.disabled = true;
                pumpOnOffToggle.textContent = 'Off';  // Reset the pump On/Off button to Off
                pumpOnOffToggle.classList.remove('on');
                pumpOnOffToggle.classList.add('off');
            }
            updatePumpState(this.id);    
        });
        
        const pumpOnOffToggle = document.getElementById("pumpOnOffToggle_" + index);
        pumpOnOffToggle.addEventListener('click', function() {
            if (this.textContent === 'Off') {
                this.textContent = 'On';
                this.classList.remove('off');
                this.classList.add('on');
            } else {
                this.textContent = 'Off';
                this.classList.remove('on');
                this.classList.add('off');
            }
            updatePumpState(this.id);
        });
        }
});
