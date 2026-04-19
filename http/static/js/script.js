let log = console.log;
var logDataIntervalTimer = undefined;
let ids = [];


// Polling function
function pollStatus() {
    log("pollStatus");
    fetch('/status')
        .then(result => result.json())
        .then(data => {
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
            
            for (const id of ["light", "heater"]) {
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
            log(data);
        });
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

    setInterval(pollStatus, 500);
    pollStatus();
});
