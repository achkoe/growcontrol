
function callServerEveryTwoSeconds() {
    const urlUpdate = `/update`;


    function makeHttpRequest() {
        fetch(urlUpdate)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();  // Change to response.json() if expecting JSON
            })
            .then(data => {
                console.log('Success:', data);
                console.log('humidity:', data.humidity);
                var e;
                e = document.getElementById("humidity");
                e.innerText = data["humidity"];
                e = document.getElementById("temperature");
                e.innerText = data["temperature"];
                e = document.getElementById("fan");
                e.innerText = data["fan"];
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    }

    // Call the function immediately
    makeHttpRequest();

    // Set the interval to call the function every 2 seconds (2000 milliseconds)
    setInterval(makeHttpRequest, 2000);
}

// Start the process
callServerEveryTwoSeconds();
