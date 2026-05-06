log = console.log;


function getSize() {
  return {
    width: window.innerWidth - 100,
    height: window.innerHeight - 200,
  }
}

const tthoptions = {
  title: null,
  ...getSize(),
  series: [
    {},
    {
      label: "Temperature",
      stroke: "red",
      scale: "left",
    },
    {
      label: "Humidity",
      stroke: "blue",
      scale: "right",
    },
    {
      label: "Fan",
      stroke: "green",
      scale: "third",
      value: (u, val) => val > 0.5 ? "On" : "Off"
    },
    {
      label: "Heater",
      stroke: "violet",
      scale: "fourth",
      value: (u, val) => val > 1.7 ? "On" : "Off"
    },
    {
      label: "Humidifier",
      stroke: "cyan",
      scale: "fifth",
      value: (u, val) => val > 2.7 ? "On" : "Off"
    }
  ],
  scales: {
    left: { range: [10, 40] },
    right: { range: [0, 100] },
    third: { range: [0, 10] },
    fourth: { range: [0, 10] },
    fifth: { range: [0, 10] },
  },
  axes: [
    {
      scale: "x", // x-axis
      label: "Time",
    },
    {
      scale: "left", // left y-axis
      label: "Temperature/°C",
      side: 3,  // position: left
      grid: { show: false, }
    },
    {
      scale: "right", // right y-axis
      label: "Humidity/%",
      side: 1,  // position: right
      grid: {
        show: false,
      }
    }
  ]
};
const moistureoptions = {
  title: null,
  ...getSize(),
  series: [],
  scales: {
    left: { range: [0, 100] },
    third: { range: [0, 10] },
  },
  axes: [
    {
      scale: "x", // x-axis
      label: "Time",
    },
    {
      scale: "left", // left y-axis
      label: "Moisture/%",
      side: 3,  // position: left
    },
  ]
};


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
      throw new Error(`Data status: ${data.status}`);
    } else {
      document.getElementById("r-logstatus").classList.add("hidden");
    }
    // log(data.statistics);
    for (const key in data.statistics) {
      let element = document.getElementById(key);
      if (element === undefined) continue;
      element.innerText = data.statistics[key].toFixed(1);
    }
    updateTTHGraph(data);
  } catch (error) {
    showHttpError(true, error.message);
    log(error.message);
  }
}

function updateTTHGraph(data) {
  log(data);
  if (data.plotdata[0].length < 2) return;

  dataplot.setData(data.plotdata);
  data.plotdata[4].forEach(function(element, index) {
    data.plotdata[4][index] += 1.2;
  });
  data.plotdata[5].forEach(function(element, index) {
    data.plotdata[5][index] += 2.4;
  });
  moistureplot.setData(data.moisturedata);
}

function initLogPlot() {
  const color = ["black", "blue", "red", "green"];
  moistureoptions.series.push({});
  for (index of HINT.moistures) {
    moistureoptions.series.push({
      "label": `Moisture ${index}`,
      "stroke": color[index],
      "scale": "left"
    });
  }
  dataplot = new uPlot(tthoptions, [], document.getElementById("datagraph"));
  moistureplot = new uPlot(moistureoptions, [], document.getElementById("moisturegraph"));
}