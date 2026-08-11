let placeMarkers = [];
let shelterMap;
let userMarker;
function createPlaceIcon(type) {
    let emoji = "📍";
    let color = "#64748b";

    if (type === "hospital") {
        emoji = "🏥";
        color = "#dc2626";
    } else if (type === "fire_station") {
        emoji = "🚒";
        color = "#f97316";
    } else if (type === "police") {
        emoji = "👮";
        color = "#2563eb";
    } else if (type === "user") {
        emoji = "📍";
        color = "#16a34a";
    }

    return L.divIcon({
        className: "custom-map-marker",
        html:
            "<div style='" +
            "background:" + color + ";" +
            "width:42px;" +
            "height:42px;" +
            "border-radius:50%;" +
            "display:flex;" +
            "align-items:center;" +
            "justify-content:center;" +
            "font-size:22px;" +
            "border:3px solid white;" +
            "box-shadow:0 3px 10px rgba(0,0,0,0.35);" +
            "'>" +
            emoji +
            "</div>",
        iconSize: [42, 42],
        iconAnchor: [21, 21],
        popupAnchor: [0, -22]
    });
}
function calculateDistanceMiles(lat1, lon1, lat2, lon2) {
    const earthRadiusMiles = 3958.8;

    const latDifference = (lat2 - lat1) * Math.PI / 180;
    const lonDifference = (lon2 - lon1) * Math.PI / 180;

    const firstLatitude = lat1 * Math.PI / 180;
    const secondLatitude = lat2 * Math.PI / 180;

    const a =
        Math.sin(latDifference / 2) * Math.sin(latDifference / 2) +
        Math.cos(firstLatitude) *
        Math.cos(secondLatitude) *
        Math.sin(lonDifference / 2) *
        Math.sin(lonDifference / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return earthRadiusMiles * c;
}


function startShelterMap() {
    const mapElement = document.getElementById("map");

    if (!mapElement) {
        console.error("The map element was not found.");
        return;
    }

    shelterMap = L.map("map").setView([42.28, -83.74], 10);

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors"
        }
    ).addTo(shelterMap);

    if (!navigator.geolocation) {
        alert("Your browser does not support location services.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        showShelterLocation,
        showShelterError
    );
}

function showShelterLocation(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    shelterMap.setView([latitude, longitude], 14);

    userMarker = L.marker([latitude, longitude], { icon: createPlaceIcon("user") })
        .addTo(shelterMap)
        .bindPopup("📍 You are here")
        .openPopup();

    loadNearbyPlaces(latitude, longitude);
}

function showShelterError(error) {
    if (error.code === 1) {
        alert("Location permission was denied. Please allow location access.");
    } else if (error.code === 2) {
        alert("Your location is currently unavailable.");
    } else if (error.code === 3) {
        alert("The location request took too long. Please try again.");
    } else {
        alert("Unable to find your location.");
    }
}

async function loadNearbyPlaces(latitude, longitude) {
    try {
        const url =
            "/api/places?lat=" + latitude +
            "&lon=" + longitude;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Unable to load nearby places.");
        }

        const places = await response.json();

        if (places.length === 0) {
            alert("No nearby emergency resources were found.");
            return;
        }

        places.forEach(function (place) {
            const distanceMiles = calculateDistanceMiles(
                latitude,
                longitude,
                place.lat,
                place.lon
            ).toFixed(1);

            let icon = "📍";

            if (place.type === "hospital") {
                icon = "🏥";
            } else if (place.type === "fire_station") {
                icon = "🚒";
            } else if (place.type === "police") {
                icon = "👮";
            }

            const marker = L.marker([place.lat, place.lon], { icon: createPlaceIcon(place.type) })
                .addTo(shelterMap)
                .bindPopup(
                    "<strong>" + icon + " " + place.name + "</strong><br>" +

                    "🏷️ " + place.type.replace("_", " ") + "<br>" +
                    "📏 " + distanceMiles + " miles away<br><br>" +

                    (place.address
                        ? "📍 " + place.address + "<br>"
                        : "") +

                    (place.phone
                        ? "☎️ <a href='tel:" + place.phone + "'>" +
                        place.phone + "</a><br>"
                        : "") +

                    (place.website
                        ? "<a href='" + place.website +
                        "' target='_blank'>🌐 Visit Website</a><br>"
                        : "") +

                    "<br><a href='https://www.google.com/maps/dir/?api=1&destination=" +
                    place.lat + "," + place.lon +
                    "' target='_blank'>🧭 Get Directions</a>"
                );

            placeMarkers.push(marker);

        });
        const allMarkers = [userMarker, ...placeMarkers];

        const markerGroup = L.featureGroup(allMarkers);
        shelterMap.fitBounds(markerGroup.getBounds(), {
            padding: [40, 40]
        });
    } catch (error) {
        console.error(error);
        alert("Nearby places could not be loaded.");
    }
}


startShelterMap();
