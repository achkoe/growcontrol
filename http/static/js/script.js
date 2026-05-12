let log = console.log;
var logDataIntervalTimer = undefined;
let ids = [];
let invalid_time_settings_count = 0

function showHttpError(show, message) {
    if (show === false) {
        for (const element of document.querySelectorAll(".r-httpstatus")) {
            element.classList.add("hidden");
        }
        return;
    }
    for (const element of document.querySelectorAll(".r-httpstatus")) {
        element.classList.remove("hidden");
    }
    for (const element of document.querySelectorAll(".d-httpstatus")) {
        element.innerText = message;
    }
}


// Polling function
async function pollStatus() {
    try {
        response = await fetch('/status');
        if (!response.ok) {
            showHttpError(true, response.status);
            throw new Error(`Response status: ${response.status}`);
        } else {
            showHttpError(false, null);
        }
        const data = await response.json();
        // log(data);
        document.getElementById("d-time").innerText = data.time;
        
        for (const id of ["temperature", "humidity"]) {
            document.getElementById(`d-${id}`).innerText = Number.parseFloat(data[id]).toFixed(1);
            let element = document.getElementById(`s-${id}`);
            element.classList.remove("status-below", "status-above");
            if (data[`${id}-status`] == "below") {
                element.classList.add("status-below");
                element.innerText = "below";
            } else if (data[`${id}-status`] == "above") {
                element.classList.add("status-above");
                element.innerText = "above";
            } else {
                element.innerText = "";
            }
        }
        
        for (const id of HINT.moistures) {
            document.getElementById(`moisture-${id}`).innerText = Number.parseFloat(data.moisture[id - 1]).toFixed(1);
            let element = document.getElementById(`moisture-status-${id}`);
            element.classList.remove("status-below", "status-above", "status-okay");
            element.innerText = data["moisture-status"][id - 1] != "okay" ? data["moisture-status"][id - 1] : "";
            element.classList.add(`status-${data["moisture-status"][id - 1]}`)
        }

        for (const id of ["waterlevel"]) {
            let element = document.getElementById(`d-${id}`);
            const text = {0: "critical", 1: "low", 2: "medium", 3: "full", "?": "?"}
            element.innerText = text[data[id]];
            for (const [key, value] of Object.entries(text)) {
                element.classList.remove(`status-${value}`);
            }
            element.classList.add(`status-${text[data[id]]}`);
        }

        for (const id of ["sensorstatus", "actorstatus"]) {
            let element = document.getElementById(`d-${id}`);
            element.innerText = data[id];
            if (data[id] != "ok") 
                document.getElementById(`r-${id}`).classList.remove("hidden")
            else
                document.getElementById(`r-${id}`).classList.add("hidden")
        }
        
        let items = ["light", "heater", "fan", "humidifier", "exhaustairfan"]
        for (const id of HINT.pumps) items.push(`pump${id}`);
        for (const id of items) {
            let mode = document.getElementById(`btn-a-${id}`);
            let control = document.getElementById(`btn-s-${id}`);
            if (data[`${id}-on`]) {
                control.innerText = "On";
                control.classList.remove("btn-off");
                control.classList.add("btn-on");
            } else {
                control.innerText = "Off";
                control.classList.remove("btn-on");
                control.classList.add("btn-off");
            }
            if (data[`${id}-mode`] == "auto") {
                mode.innerText = "Auto";
                mode.classList.remove("btn-manual");
                mode.classList.add("btn-auto");
                control.disabled = true;
                control.classList.remove("btn-on", "btn-off");
                control.classList.add("btn-disabled");
            } else {
                mode.innerText = "Manual";
                mode.classList.remove("btn-auto");
                mode.classList.add("btn-manual");
                control.disabled = false;
                control.classList.remove("btn-disabled");
            }
        }
    } catch (error) {
        console.error(error.message);
        showHttpError(true, error.message);
    }
}

async function fetchWatchdog(url) {
  showHttpError(false, null);
  try {
    response = await fetch(url);
    log(response);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }
    const data = await response.json();
    if (data.status != "ok") {
      throw new Error(`Data status: ${data.status}`);
    }
    document.getElementById("watchdog").innerText = data.watchdog;
  } catch (error) {
    showHttpError(true, error.message);
    log(error.message);
  }
}

window.addEventListener("load", (event) => {
    console.log("page is fully loaded");

    for (const element of document.querySelectorAll(".button")) {
        element.addEventListener("click", async function (event) {
            let buttonlist = document.querySelectorAll(".button");
            buttonlist.forEach((element) => {
                log("1");
                element.classList.add("btn-disabled");
                element.disabled = true;
            });

            response = await fetch(`/buttonclick`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "id": this.id, "classlist": this.classList.value })
            });
            const result = await response.json();
            log(result);
            buttonlist.forEach((element) => {
                log("2");
                element.classList.remove("btn-disabled");
                element.disabled = false;
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
            document.getElementById(id).style.display = "block";

            if (id == "logdata") {
                fetchLogData('/logdata');
                logDataIntervalTimer = setInterval(fetchLogData, 2000, '/logdata');
            } else {
                if (logDataIntervalTimer !== undefined) {
                    clearInterval(logDataIntervalTimer);
                }
            }
            if (id == "watchdog") {
                fetchWatchdog('/watchdog');
                watchdogIntervalTimer = setInterval(fetchWatchdog, 2000, '/watchdog');
            } else {
                if (watchdogIntervalTimer !== undefined) {
                    clearInterval(watchdogIntervalTimer);
                }
            }
        });
    }
    
    const timeinputs = document.querySelectorAll(".timeinput");
    for (const timeinput of timeinputs) {
        timeinput.addEventListener("input", async function(event) {
            try {
                response = await fetch('/verifytimeinput', {
                    headers: {"Content-Type": "application/json"},
                    method: "POST",
                    body: JSON.stringify({"value": timeinput.value, "element": timeinput.id})
                });
                if (!response.ok) {
                    throw new Error(`Response status: ${response.status}`);
                }
                const data = await response.json();
                log(data);
                timeinput.title = data.title;
                if (!data.valid) {
                    timeinput.classList.add("status-invalid");
                    invalid_time_settings_count += 1;
                } else {
                    timeinput.classList.remove("status-invalid");
                    invalid_time_settings_count -= 1;
                }
                let element = document.getElementById("submit");
                element.disabled = invalid_time_settings_count > 0;
                if (invalid_time_settings_count <= 0)
                    element.classList.remove("btn-disabled");
                else
                    element.classList.add("btn-disabled")   
            }
            catch (error) {
                log(error);
            }
        });
    }

    initLogPlot();

    setInterval(pollStatus, 500);
    pollStatus();
});
