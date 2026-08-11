const button = document.getElementById("locationBtn");
const result = document.getElementById("locationResult");

let map;
let marker;

button.addEventListener("click", function () {
    result.innerHTML = "Finding your location...";

    if (!navigator.geolocation) {
        result.innerHTML =
            "Your browser does not support location services.";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        showPosition,
        showError
    );
});

function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    result.innerHTML = `
        <h3>Your Current Location</h3>
        <p><strong>Latitude:</strong> ${latitude}</p>
        <p><strong>Longitude:</strong> ${longitude}</p>
    `;

    if (!map) {
        map = L.map("map").setView([latitude, longitude], 14);

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 19,
                attribution: "&copy; OpenStreetMap contributors"
            }
        ).addTo(map);
    } else {
        map.setView([latitude, longitude], 14);
    }

    if (marker) {
        marker.setLatLng([latitude, longitude]);
    } else {
        marker = L.marker([latitude, longitude])
            .addTo(map)
            .bindPopup("You are here")
            .openPopup();
    }
}

function showError(error) {
    if (error.code === 1) {
        result.innerHTML =
            "Location permission was denied. Please allow location access.";
    } else if (error.code === 2) {
        result.innerHTML =
            "Your location is currently unavailable.";
    } else if (error.code === 3) {
        result.innerHTML =
            "The location request took too long. Please try again.";
    } else {
        result.innerHTML =
            "Unable to find your location.";
    }
}
async function loadNearbyPlaces() {

    const response = await fetch("/api/places");

    const places = await response.json();

    places.forEach(place => {

        L.marker([place.lat, place.lon])
            .addTo(shelterMap)
            .bindPopup(
                "<b>" + place.name + "</b><br>" + place.type
            );

    });

}
