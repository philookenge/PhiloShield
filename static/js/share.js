const getLocationButton =
    document.getElementById("getLocationButton");

const locationResult =
    document.getElementById("locationResult");

let emergencyMessage = "";
let mapLink = "";


getLocationButton.addEventListener("click", function () {
    locationResult.innerHTML =
        "<p>📍 Finding your current location...</p>";

    if (!navigator.geolocation) {
        locationResult.innerHTML =
            "<p>Your browser does not support location services.</p>";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        showLocation,
        showLocationError,
        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
});


function showLocation(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    mapLink =
        "https://www.google.com/maps?q=" +
        latitude + "," + longitude;

    emergencyMessage =
        "🚨 I may need help. My current location is: " +
        mapLink;

    const encodedMessage =
        encodeURIComponent(emergencyMessage);

    const encodedSubject =
        encodeURIComponent("Emergency Location");

    locationResult.innerHTML =
        "<div class='share-location-card'>" +

        "<h2>📍 Location Found</h2>" +

        "<p><strong>Latitude:</strong> " +
        latitude.toFixed(6) +
        "</p>" +

        "<p><strong>Longitude:</strong> " +
        longitude.toFixed(6) +
        "</p>" +

        "<a class='map-button' href='" +
        mapLink +
        "' target='_blank'>" +
        "🗺️ Open in Google Maps</a>" +

        "<br><br>" +

        "<button type='button' onclick='copyLocation()'>" +
        "📋 Copy Location</button>" +

        "<a class='share-button sms-button' href='sms:?body=" +
        encodedMessage +
        "'>💬 Send by Text</a>" +

        "<a class='share-button email-button' href='mailto:?subject=" +
        encodedSubject +
        "&body=" +
        encodedMessage +
        "'>📧 Send by Email</a>" +

        "<a class='share-button whatsapp-button' " +
        "href='https://wa.me/?text=" +
        encodedMessage +
        "' target='_blank'>" +
        "🟢 Share on WhatsApp</a>" +

        "<button type='button' onclick='shareLocation()'>" +
        "📤 More Sharing Options</button>" +

        "</div>";
}


function showLocationError(error) {
    if (error.code === 1) {
        locationResult.innerHTML =
            "<p>Location permission was denied. " +
            "Please allow location access.</p>";
    } else if (error.code === 2) {
        locationResult.innerHTML =
            "<p>Your current location is unavailable.</p>";
    } else if (error.code === 3) {
        locationResult.innerHTML =
            "<p>The location request took too long. Please try again.</p>";
    } else {
        locationResult.innerHTML =
            "<p>Your location could not be determined.</p>";
    }
}


async function copyLocation() {
    try {
        await navigator.clipboard.writeText(emergencyMessage);
        alert("Location copied successfully!");
    } catch (error) {
        console.error(error);
        alert("The location could not be copied.");
    }
}


async function shareLocation() {
    if (!navigator.share) {
        alert(
            "Your browser does not support the sharing menu. " +
            "Use Text, Email, WhatsApp, or Copy Location instead."
        );
        return;
    }

    try {
        await navigator.share({
            title: "Emergency Location",
            text: emergencyMessage,
            url: mapLink
        });
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error(error);
        }
    }
}
