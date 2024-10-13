
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
                var e;
                ["fan", "fan_mode", "light_1", "light_2", "time"].forEach(function(field) {
                    e = document.getElementById(field);
                    e.innerText = data[field];
                });
                
                e = document.getElementById("fan_mode");
                if (data["fan_mode"] == "Manual") {
                    fan_mode.classList.remove('auto');
                    fan_mode.classList.add('manual');
                    fanOnOffToggle.disabled = false;
                } else {
                    fan_mode.classList.remove('manual');
                    fan_mode.classList.add('auto');
                    fanOnOffToggle.disabled = true;        
                }
                
                e = document.getElementById("fanOnOffToggle");
                if (data["fan"] == "ON") {
                    fanOnOffToggle.textContent = 'On';
                    fanOnOffToggle.classList.remove('off');
                    fanOnOffToggle.classList.add('on');
                } else {
                    fanOnOffToggle.textContent = 'Off';
                    fanOnOffToggle.classList.remove('on');
                    fanOnOffToggle.classList.add('off');
                }

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
    const lightToggle = document.getElementById('lightToggle');
    const light1Toggle = document.getElementById('light1Toggle');
    const light2Toggle = document.getElementById('light2Toggle');

    
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

    function updateLightState() {
        const state = {
            light: lightToggle.textContent === 'Manual' ? 'Manual' : 'Auto',
            light1: light1Toggle.textContent === 'On' ? 'On' : 'Off',
            light2: light2Toggle.textContent === 'On' ? 'On' : 'Off'
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

    lightToggle.addEventListener('click', function() {
        if (lightToggle.textContent === 'Auto') {
            lightToggle.textContent = 'Manual';
            lightToggle.classList.remove('auto');
            lightToggle.classList.add('manual');
            light1Toggle.disabled = false;
            light2Toggle.disabled = false;
        } else {
            lightToggle.textContent = 'Auto';
            lightToggle.classList.remove('manual');
            lightToggle.classList.add('auto');
            light1Toggle.disabled = true;
            light2Toggle.disabled = true;
            light1Toggle.textContent = 'Off';  // Reset the Light1 button to Off
            light1Toggle.classList.remove('on');
            light1Toggle.classList.add('off');
            light2Toggle.textContent = 'Off';  // Reset the Light2 button to Off
            light2Toggle.classList.remove('on');
            light2Toggle.classList.add('off');
        }
        updateLightState();
    });

    light1Toggle.addEventListener('click', function() {
        if (light1Toggle.textContent === 'Off') {
            light1Toggle.textContent = 'On';
            light1Toggle.classList.remove('off');
            light1Toggle.classList.add('on');
        } else {
            light1Toggle.textContent = 'Off';
            light1Toggle.classList.remove('on');
            light1Toggle.classList.add('off');
        }
        updateLightState();
    });
    
    light2Toggle.addEventListener('click', function() {
        if (light2Toggle.textContent === 'Off') {
            light2Toggle.textContent = 'On';
            light2Toggle.classList.remove('off');
            light2Toggle.classList.add('on');
        } else {
            light2Toggle.textContent = 'Off';
            light2Toggle.classList.remove('on');
            light2Toggle.classList.add('off');
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
