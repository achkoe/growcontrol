let log = console.log;
var logDataIntervalTimer = undefined;
let ids = [];


// Polling function
function pollStatus() {
    fetch('/status')
        .then(res => res.json())
        .then(data => {
            // console.log(data);
            for (id of [ "value-temperature", "value-humidity"]) {
                let e = document.getElementById(id)
                e.innerText = parseFloat(data[id]).toFixed(1);
            }
            for (id of ["value-time", "value-watersupplylevel", "value-fan", "value-heater", "value-light", "value-humidifier", "value-pump"]) {
                let e = document.getElementById(id)
                e.innerText = data[id];
                if (["ON", "OFF"].includes(data[id])) {
                    e.parentElement.classList.remove("on");
                    e.parentElement.classList.remove("off");
                    e.parentElement.classList.add(data[id].toLowerCase());
                }
            }
            for (const key of ["temperature", "humidity"]) {
                let e = document.getElementById(`value-${key}`).parentElement;
                e.classList.remove("tohigh");
                e.classList.remove("tolow");
                e.classList.remove("acceptable");
                if (data[`value-${key}`] >= data["settings"][`${key}_high_critical_level`]) {
                    e.classList.add("tohigh");
                    e.title = "to high"
                } else if (data[`value-${key}`] <= data["settings"][`${key}_low_critical_level`]) {
                    e.classList.add("tolow");
                    e.title = "to low";
                } else {
                    e.classList.add("acceptable");
                }
            }
            for (id of ids) {
                var e;
                e = document.getElementById(id);
                e.innerText = data[id];
                let type = id.split("-")[1];
                if (type == "mode") {
                    if (data[id] == "Auto") {
                        e.classList.remove("modemanual");
                        e.classList.add("modeauto");
                    } else {
                        e.classList.add("modemanual");
                        e.classList.remove("modeauto");
                    }
                    let onoff = `${id.split("-")[0]}-onoff`;
                    e = document.getElementById(onoff);
                    if (data[id] == "Manual") {
                        e.disabled = false;
                    } else {
                        e.disabled = true;
                    }
                } else if (type == "onoff") {
                    e.classList.remove("on");
                    e.classList.remove("off");
                    e.classList.add(e.innerText.toLowerCase());
                }
            }
            // waterlevel
            {
                const id = "value-watersupplylevel";
                const obj = { 0: "critical", 1: "low", 2: "medium", 3: "full" }
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

    
    for (let index = 1; ; index++) {
        let id = `pump${index}-onoff`;
        let e = document.getElementById(id);
        if (e === null) break;
        ids.push(id);
        ids.push(`pump${index}-soilmoisture`);
    }
    ids = ids.concat(["fan-mode", "fan-onoff", "pump-mode", "pump-onoff", "heater-mode", "heater-onoff", "humidifier-mode", "humidifier-onoff", "light-mode", "light-onoff", "exhaustfan-onoff"]);
    for (const id of ids) {
        document.getElementById(id).addEventListener("click", function (event) {
            fetch(`/control`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "id": this.id })
            });
        });
    }

    // tab handling
    const tabs = document.querySelectorAll(".tab");
    for (const tab of tabs) {
        tab.addEventListener("click", function (event) {
            for (let tab of tabs) {
                tab.classList.remove("active");
                document.getElementById(tab.getAttribute("data-tab")).style.display = "none";
            }
            this.classList.add("active");
            let id = this.getAttribute("data-tab");
            let e = document.getElementById(id).style.display = "block";

            if (id == "logdata") {
                makeLogHttpRequest('/logdata');
                logDataIntervalTimer = setInterval(makeLogHttpRequest, 20000, '/logdata');
            } else {
                if (logDataIntervalTimer !== undefined) {
                    clearInterval(logDataIntervalTimer);
                }
            }
            if (id == "watchdog") {
                fetch("/watchdog")
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok ' + response.statusText);
                        }
                        return response.json();
                    })
                    .then(data => {
                        log(data);
                        document.getElementById("watchdog-status").innerHTML = data["watchdog"];
                    })
                    .catch(error => {
                        console.error('There has been a problem with your fetch operation:', error);
                    });
            }
        });
    }

    tthplot = new uPlot(tthoptions, [], document.getElementById("tthgraph"));
    for (let index = 1; ; index++) {
        let e = document.getElementById("moisturegraph_" + index);
        if (e === null) break;
        moistureplot[index] = new uPlot(moistureoptions, [], e);
    }

    setInterval(pollStatus, 500);
    pollStatus();
});
