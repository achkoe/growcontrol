log = console.log;

async function fetchLogData(url) {
  showHttpError(false, null);
  try {
    response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }
    const data = await response.json();
    if (data.status != "ok") {
      document.getElementById("r-logstatus").classList.remove("hidden");
      document.getElementById("d-logstatus").innerText = data.status;
    } else {
      document.getElementById("r-logstatus").classList.add("hidden");
    }
    log(data.statistics);
    for (const key in data.statistics) {
      let element = document.getElementById(key);
      if (element === undefined) continue;
      element.innerText = data.statistics[key]
      log(key);  
    }
  } catch (error) {
    showHttpError(true, error.message);
    log(error.message);
  }
}