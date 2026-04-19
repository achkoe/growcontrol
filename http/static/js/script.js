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
                    
                }
                
            }
            log(data);
        });
}

window.addEventListener("load", (event) => {
    console.log("page is fully loaded");

    setInterval(pollStatus, 500);
    pollStatus();
});
