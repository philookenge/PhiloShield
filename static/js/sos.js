const sosButton = document.getElementById("sosButton");
const sosStatus = document.getElementById("sosStatus");
const alarm = new Audio("/static/audio/alarm.wav");
alarm.loop = true;

sosButton.addEventListener("click", activateSOS);

function activateSOS() {
    alarm.currentTime = 0;
    alarm.play();

    sosStatus.innerHTML =
        "<h2>🚨 SOS ACTIVATED</h2>" +
        "<p>Finding your location...</p>";

    if (!navigator.geolocation) {
        sosStatus.innerHTML =
            "<p>Your browser does not support location services.</p>";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        showSOSLocation,
        showSOSError
    );
}

function showSOSLocation(position) {

    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    sosStatus.innerHTML =
        "<h2>🚨 SOS ACTIVATED</h2>" +

        "<p><strong>Latitude:</strong> " +
        latitude.toFixed(6) +
        "</p>" +

        "<p><strong>Longitude:</strong> " +
        longitude.toFixed(6) +
        "</p>" +

        "<p>☎️ Call 911 immediately if you are in danger.</p>" +

        "<a class='call-button' href='tel:911'>" +
        "📞 Call 911</a>" +

        "<br><br>" +

        "<a class='map-button' href='https://www.google.com/maps?q=" +
        latitude + "," + longitude +
        "' target='_blank'>" +
        "📍 Open My Location in Google Maps</a>";
}

function showSOSError(error) {

    if (error.code === 1) {
        sosStatus.innerHTML =
            "<p>Location permission was denied.</p>";
    } else if (error.code === 2) {
        sosStatus.innerHTML =
            "<p>Your location is unavailable.</p>";
    } else if (error.code === 3) {
        sosStatus.innerHTML =
            "<p>Location request timed out.</p>";
    } else {
        sosStatus.innerHTML =
            "<p>Unable to determine your location.</p>";
    }
}
