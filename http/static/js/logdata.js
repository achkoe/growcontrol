log = console.log;
const tthoptions = {
  title: null,
  width: 1110,
  height: 480,
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
    width: 1110,
    height: 480,
    series: [],
    scales: {
        left: { range: [0, 100]},
        third: { range: [0, 10]},
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
    updateTTHGraph(data.control);
  } catch (error) {
    showHttpError(true, error.message);
    log(error.message);
  }
}

function updateTTHGraph(data) {
  if (data.length < 2) return;

  var plotdata = [[], [], [], [], [], []];
  for (let item of data) {
    plotdata[0].push(item.time);       // currenttime
    plotdata[1].push(item.temperature);       // temperature
    plotdata[2].push(item.humidity);       // humidity
    plotdata[3].push(item["fan-on"] ? 1 : 0);       // fan
    plotdata[4].push(item["heater-on"] ? 2.2 : 1.2); // heater
    plotdata[5].push(item["humidifier-on"] ? 3.4 : 2.4); // humidifier
  }
  dataplot.setData(plotdata);

  plotdata = [[]];
  for (index in HINT.moistures) {
    plotdata.push([]);
  }
  for (const item of data) {
    plotdata[0].push(item.time);
    for (index of HINT.moistures) {
      plotdata[index].push(item.moisture[index - 1]);
    }
  }
  moistureplot.setData(plotdata);
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