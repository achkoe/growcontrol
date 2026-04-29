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


