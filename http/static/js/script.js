
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
                ["humidity", "temperature", "fan", "light_1", "light_2", "time"].forEach(function(field) {
                    e = document.getElementById(field);
                    e.innerText = data[field];
                });
                // e = document.getElementById("temperature");
                // e.innerText = data["temperature"];
                // e = document.getElementById("fan");
                // e.innerText = data["fan"];
                // e = document.getElementById("light_1");
                // e.innerText = data["light_1"];
                // e = document.getElementById("light_2");
                // e.innerText = data["light_2"];
                // e = document.getElementById("time");
                // e.innerText = data["time"];
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


document.addEventListener('DOMContentLoaded', () => {
    const toggleFanModeButton = document.getElementById('toggleFanModeButton');
    const toggleFanModeCaption = document.getElementById('toggleFanModeCaption');
    const toggleFanOnOffButton = document.getElementById('toggleFanOnOffButton');
    const toggleFanOnOffCaption = document.getElementById('toggleFanOnOffCaption');
    
    toggleFanModeButton.addEventListener('click', () => {
        toggleFanModeButton.classList.toggle('active');
        const isActive = toggleFanModeButton.classList.contains('active');
        const isOn = toggleFanOnOffButton.classList.contains('active');

        if (isActive) {
            toggleFanOnOffButton.classList.remove('disabled');
        } else {
            toggleFanOnOffButton.classList.add('disabled');
        }
        
        // Update the caption based on the toggle state
        toggleFanModeCaption.textContent = isActive ? 'Manual' : 'Auto';
        
        // Prepare data to send to the server
        const data = { toggleState: isActive, isOn: isOn };
        
        // Send the state to the server using Fetch API
        fetch('/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
    
    toggleFanOnOffButton.addEventListener('click', () => {
        if (toggleFanOnOffButton.classList.contains('disabled')) return;
        toggleFanOnOffButton.classList.toggle('active');
        const isActive = toggleFanModeButton.classList.contains('active');
        const isOn = toggleFanOnOffButton.classList.contains('active');
        
        // Update the caption based on the toggle state
        toggleFanOnOffCaption.textContent = isOn ? 'On' : 'Off';

        // Prepare data to send to the server
        const data = { toggleState: isActive, isOn: isOn };
        
        // Send the state to the server using Fetch API
        fetch('/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});