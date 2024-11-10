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
      },
    {
        label: "Heater",
        stroke: "violet",
        scale: "fourth",
      }
    ],
    scales: {
        left: { range: [10, 40]},
        right: { range: [0, 100]},
        third: { range: [0, 10]},
        fourth: { range: [0, 10]},
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
          grid: { show: false,}
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
    series: [
      {},
      {
        label: "Moisture",
        stroke: "blue",
        scale: "left",
    },
    {
        label: "Pump",
        stroke: "green",
        scale: "third",
      }
    ],
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
const initialData = [
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
];
var tthplot;
var moistureplot = {};

window.onload = function() {
    tthplot = new uPlot(tthoptions, [], document.getElementById("tthgraph"));
    for (index = 1; index < 10; index++) {
        let e = document.getElementById("moisturegraph_" + index);
        if (e === null) break;
        moistureplot[index] = new uPlot(moistureoptions, [], e);
    }
    // Start the process
    callLogDataUpdate();
}

function callLogDataUpdate() {
    const urlUpdate = `/logdata`;


    function makeHttpRequest() {
        fetch(urlUpdate)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();  // Change to response.json() if expecting JSON
            })
            .then(data => {
                // console.log('data:', data["m"]);
                //! var text = "";
                // (currenttime, temperature, humidity, fan, heater)
                var plotdata = [[], [], [], [], []];
                for (let tuple of data["tth"]) {
                    //! text += "" + tuple[0] + "  " + tuple[1] + "  " + tuple[2] + "  " + tuple[3] + "\n";
                    plotdata[0].push(tuple[0]);
                    plotdata[1].push(tuple[1]);
                    plotdata[2].push(tuple[2]);
                    plotdata[3].push(tuple[3]); // fan
                    plotdata[4].push(tuple[4] + 1.2); // heater
                }
                //! var e = document.getElementById("tthpanel");
                //! e.innerText = text;
                
                if (data["tth"].length >= 2) {
                    tthplot.setData(plotdata);
                }
                
                for (let [key, value] of Object.entries(data["m"])) {
                    //! text = "";
                    plotdata = [[], [], []];
                    for (let tuple of value) {
                        //! text += "" + tuple[0] + "  " + tuple[1] + "  " + tuple[2] + "\n";
                        plotdata[0].push(tuple[0]);
                        plotdata[1].push(tuple[1]);
                        plotdata[2].push(tuple[2]);
                    }
                    if (plotdata[0].length >= 2) {
                        moistureplot[key].setData(plotdata);
                    }
                    //! e = document.getElementById("moisturepanel_" + key);
                    //! e.innerText = text;
                }
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    }

    // Call the function immediately
    makeHttpRequest();

    // Set the interval to call the function every 20 seconds (20000 milliseconds)
    setInterval(makeHttpRequest, 20000);
}

