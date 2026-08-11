async function loadAlerts() {
    const alertsContainer = document.getElementById("alertsContainer");

    alertsContainer.innerHTML = "<p>Checking your location...</p>";

    if (!navigator.geolocation) {
        alertsContainer.innerHTML =
            "<p>Your browser does not support location services.</p>";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        fetchAlertsForLocation,
        showAlertsLocationError
    );
}


async function fetchAlertsForLocation(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    const alertsContainer = document.getElementById("alertsContainer");

    alertsContainer.innerHTML = "<p>Loading official alerts...</p>";

    try {
        const url =
            "/api/alerts?lat=" + latitude +
            "&lon=" + longitude;

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Emergency alerts could not be loaded."
            );
        }

        displayAlerts(data);

    } catch (error) {
        console.error(error);

        alertsContainer.innerHTML =
            "<p>Emergency alerts could not be loaded. Please try again.</p>";
    }
}


function displayAlerts(alerts) {
    const alertsContainer = document.getElementById("alertsContainer");

    if (alerts.length === 0) {
        alertsContainer.innerHTML =
            "<section class='status-card'>" +
            "<h2>✅ No Active Alerts</h2>" +
            "<p>No active National Weather Service alerts were found " +
            "for your location.</p>" +
            "</section>";

        return;
    }

    alertsContainer.innerHTML = "";

    alerts.forEach(function (alert) {
        const alertCard = document.createElement("section");
        alertCard.className = "status-card";

        alertCard.innerHTML =
            "<h2>⚠️ " + alert.event + "</h2>" +
            "<p><strong>Severity:</strong> " + alert.severity + "</p>" +
            "<p><strong>Area:</strong> " + alert.area + "</p>" +
            "<p><strong>Headline:</strong> " + alert.headline + "</p>" +
            "<p><strong>Instructions:</strong><br>" +
            alert.instruction + "</p>";

        alertsContainer.appendChild(alertCard);
    });
}


function showAlertsLocationError(error) {
    const alertsContainer = document.getElementById("alertsContainer");

    if (error.code === 1) {
        alertsContainer.innerHTML =
            "<p>Location permission was denied. Please allow location access.</p>";
    } else if (error.code === 2) {
        alertsContainer.innerHTML =
            "<p>Your location is currently unavailable.</p>";
    } else if (error.code === 3) {
        alertsContainer.innerHTML =
            "<p>The location request took too long. Please try again.</p>";
    } else {
        alertsContainer.innerHTML =
            "<p>Your location could not be determined.</p>";
    }
}


loadAlerts();
