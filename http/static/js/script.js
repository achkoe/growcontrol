let log = console.log;
var logDataIntervalTimer = undefined;
let ids = [];


// Polling function
async function pollStatus() {
    let relement = document.getElementById("r-httpstatus");
    let delement = document.getElementById("d-httpstatus");
    try {
        response = await fetch('/status');
        if (!response.ok) {
            delement.innerText = response.status;
            relement.classList.remove("hidden");
            throw new Error(`Response status: ${response.status}`);
        } else {
            delement.innerText = response.status;
            relement.classList.add("hidden");
        }
        const data = await response.json();
        // log(data);
        document.getElementById("d-time").innerText = data.time;
        
        for (const id of ["temperature", "humidity"]) {
            document.getElementById(`d-${id}`).innerText = data[id];
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
            document.getElementById(`moisture-${id}`).innerText = data.moisture[id - 1];
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
            //log(`${id}-on`);
            if (`${id}-on` == "exhaustairfan-on") {
                log(data[`${id}-on`]);

            }
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
        delement.innerText = error.message;
        relement.classList.remove("hidden");

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

    {

    }

    setInterval(pollStatus, 500);
    pollStatus();
});
