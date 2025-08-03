let log = console.log;

// Polling function
function pollStatus() {
    fetch('/status')
        .then(res => res.json())
        .then(data => {
            // console.log(data);
            for (id of ["value-time", "value-temperature", "value-humidity", "value-humidifier", "value-watersupplylevel", "value-fan", "value-heater", "value-light"]) {
                document.getElementById(id).innerText = data[id];
            }
            for (id of ["fan-mode", "fan-onoff", "heater-mode", "heater-onoff", "humidifier-mode", "humidifier-onoff", "light-mode", "light-onoff", "exhaustfan-onoff"]) {
                var e;
                e = document.getElementById(id);
                e.innerText = data[id];
                if (id.split("-")[1] == "mode"){
                    let onoff = `${id.split("-")[0]}-onoff`;
                    e = document.getElementById(onoff);
                    if (data[id] == "Manual") {
                        e.disabled = false;
                    } else {
                        e.disabled = true;
                    }
                }
            }
        });
}

window.addEventListener("load", (event) => {
    console.log("page is fully loaded");
    
    for (id of ["fan-mode", "fan-onoff", "heater-mode", "heater-onoff", "humidifier-mode", "humidifier-onoff", "light-mode", "light-onoff", "exhaustfan-onoff"]) {
        document.getElementById(id).addEventListener("click", function(event) {
            log(this.id);
            fetch(`/control`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({"id": this.id})
            });
        });
    }
    setInterval(pollStatus, 1500);
    pollStatus();
    
    if (false) {
        let e = document.getElementById("light-mode");
        e.addEventListener("click", function(event) {
            if (this.innerText == "Auto") {
                this.innerText = "Manual";
                document.getElementById("light-onoff").disabled = false;
            } else {
                this.innerText = "Auto";
                document.getElementById("light-onoff").disabled = true;
            }
        });
    }
});
