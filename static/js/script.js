// // static/js/script.js
// document.addEventListener('DOMContentLoaded', function() {
//     console.log("Crop Yield Predictor UI Initialized");

//     // Example: Smooth scroll for flash messages if they exist
//     const flashMessages = document.querySelector('.flash-messages');
//     if (flashMessages && flashMessages.children.length > 0) {
//         flashMessages.scrollIntoView({ behavior: 'smooth', block: 'start' });
//     }

//     // You can add more client-side interactions here:
//     // - Real-time input validation (e.g., numeric ranges)
//     // - Dynamic hiding/showing of certain fields based on selections
//     // - AJAX form submission for a single-page app feel (more advanced)

//     const form = document.getElementById('predictionForm');
//     if(form) {
//         form.addEventListener('submit', function() {
//             const predictButton = form.querySelector('.btn-predict');
//             if(predictButton) {
//                 predictButton.innerHTML = 'Predicting... <span class="spinner"></span>'; // Add a simple spinner or loading text
//                 predictButton.disabled = true;
//             }
//         });
//     }

//     // Simple spinner CSS (can be added to style.css or here as a style tag for simplicity if preferred)
//     const style = document.createElement('style');
//     style.innerHTML = `
//         .spinner {
//             display: inline-block;
//             width: 1em;
//             height: 1em;
//             border: 2px solid rgba(255,255,255,0.3);
//             border-radius: 50%;
//             border-top-color: #fff;
//             animation: spin 1s ease-infinite;
//             vertical-align: middle;
//             margin-left: 5px;
//         }
//         @keyframes spin {
//             to { transform: rotate(360deg); }
//         }
//     `;
//     document.head.appendChild(style);

// })



// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("Crop Yield Predictor UI Initialized for auto-fill");

    const stateInput = document.getElementById('state');
    const rainfallInput = document.getElementById('rainfall');
    const temperatureInput = document.getElementById('temperature');
    const rainfallNotification = document.getElementById('rainfall-notification');
    const temperatureNotification = document.getElementById('temperature-notification');

    if (stateInput && rainfallInput && temperatureInput) {
        stateInput.addEventListener('change', function() { // 'input' event can also be used
            const selectedState = this.value;
            // Clear previous notifications and values if state is cleared or invalid
            rainfallNotification.textContent = '';
            temperatureNotification.textContent = '';

            if (selectedState) {
                fetch(`/get_climate_data/${selectedState}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        let rainMsg = 'State data not found for rainfall.';
                        let tempMsg = 'State data not found for temperature.';

                        if (data.rainfall !== null && data.rainfall !== undefined) {
                            rainfallInput.value = data.rainfall;
                            rainMsg = `Rainfall auto-filled for ${selectedState}.`;
                        } else {
                            rainfallInput.value = ''; // Clear if no data
                        }
                        rainfallNotification.textContent = rainMsg;
                        rainfallNotification.style.color = (data.rainfall !== null && data.rainfall !== undefined) ? 'green' : 'orange';


                        if (data.temperature !== null && data.temperature !== undefined) {
                            temperatureInput.value = data.temperature;
                            tempMsg = `Temperature auto-filled for ${selectedState}.`;
                        } else {
                            temperatureInput.value = ''; // Clear if no data
                        }
                        temperatureNotification.textContent = tempMsg;
                        temperatureNotification.style.color = (data.temperature !== null && data.temperature !== undefined) ? 'green' : 'orange';

                    })
                    .catch(error => {
                        console.error('Error fetching climate data:', error);
                        rainfallInput.value = '';
                        temperatureInput.value = '';
                        rainfallNotification.textContent = 'Could not load rainfall data.';
                        rainfallNotification.style.color = 'red';
                        temperatureNotification.textContent = 'Could not load temperature data.';
                        temperatureNotification.style.color = 'red';
                    });
            } else {
                // State input is empty, clear the fields
                rainfallInput.value = '';
                temperatureInput.value = '';
            }
        });
    }

    // Keep the form submission spinner logic if you had it
    const form = document.getElementById('predictionForm');
    if (form) {
        form.addEventListener('submit', function() {
            const predictButton = form.querySelector('.btn-predict');
            if (predictButton) {
                // Simple loading text, you can enhance this with a real spinner
                predictButton.innerHTML = 'Predicting... <span class="spinner-small"></span>';
                predictButton.disabled = true;
            }
        });
    }
    // Add a small spinner style if you don't have one
    const style = document.createElement('style');
    style.innerHTML = `
        .auto-fill-notification {
            font-size: 0.8em;
            margin-top: 4px;
            display: block;
        }
        .spinner-small {
            display: inline-block;
            width: 1em;
            height: 1em;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-infinite;
            vertical-align: middle;
            margin-left: 5px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
});