let log = console.log;

// Polling function
function pollStatus() {
    fetch('/status')
        .then(res => res.json())
        .then(data => {
            // console.log(data);
            for (id of ["value-time", "value-temperature", "value-humidity", "value-humidifier", "value-watersupplylevel", "value-fan", "value-heater", "value-light"]) {
                let e = document.getElementById(id)
                e.innerText = data[id];
                if (["ON", "OFF"].includes(data[id])) {
                    e.parentElement.classList.remove("on");   
                    e.parentElement.classList.remove("off");
                    e.parentElement.classList.add(data[id].toLowerCase());
                }
            }
            for (const key of ["temperature", "humidity"]) {
                let e= document.getElementById(`value-${key}`).parentElement;
                e.classList.remove("tohigh");
                e.classList.remove("tolow");
                e.classList.remove("acceptable");
                if (data[`value-${key}`] >= data["settings"][`${key}_high_critical_level`]) {
                    e.classList.add("tohigh");
                } else if (data[`value-${key}`] <= data["settings"][`${key}_low_critical_level`]) {
                    e.classList.add("tolow");
                } else {
                    e.classList.add("acceptable");
                }
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
            // waterlevel
            {
                const id = "value-watersupplylevel";
                const obj = {0: "critical", 1: "low", 2: "medium", 3: "full"}
                let e = document.getElementById(id);
                e.innerText = data[id] in obj ? obj[data[id]] : "unknown";
                e = e.parentElement;
                for (const name of ["critical", "low", "medium", "full"]) {
                    e.classList.remove(name);
                }
                e.classList.add(obj[data[id]]);
            }
        });
}

window.addEventListener("load", (event) => {
    console.log("page is fully loaded");
    
    for (const id of ["fan-mode", "fan-onoff", "heater-mode", "heater-onoff", "humidifier-mode", "humidifier-onoff", "light-mode", "light-onoff", "exhaustfan-onoff"]) {
        document.getElementById(id).addEventListener("click", function(event) {
            fetch(`/control`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({"id": this.id})
            });
        });
    }

    const tabs = document.querySelectorAll(".tab");
    for (const tab of tabs) {
        log(tab);
        tab.addEventListener("click", function(event) {
            for (let tab of tabs) {
                tab.classList.remove("active");
                document.getElementById(tab.getAttribute("data-tab")).style.display = "none";
            }
            this.classList.add("active");
            document.getElementById(this.getAttribute("data-tab")).style.display = "block";
            fetch(`/${this.getAttribute("data-tab")}`) .then(res => res.json()) .then(data => { log(data); });            
        });
    }
    setInterval(pollStatus, 1500);
    pollStatus();
});
