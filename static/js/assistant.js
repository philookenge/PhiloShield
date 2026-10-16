const sendButton = document.getElementById("sendButton");
const userMessage = document.getElementById("userMessage");
const chatContainer = document.getElementById("chatContainer");

let userLatitude = null;
let userLongitude = null;

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLatitude = position.coords.latitude;
            userLongitude = position.coords.longitude;
            console.log("Assistant location ready");
        },
        (error) => {
            console.log("Location unavailable:", error.message);
        }
    );
}


function getUserLocation() {
    return new Promise((resolve) => {
        if (!navigator.geolocation) {
            resolve({ latitude: null, longitude: null });
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            () => {
                resolve({ latitude: null, longitude: null });
            }
        );
    });
}

sendButton.addEventListener("click", async function () {
    const message = userMessage.value.trim();

    if (message === "") {
        return;
    }

    const userText = document.createElement("p");
    userText.textContent = "You: " + message;
    chatContainer.appendChild(userText);

    userMessage.value = "";

    const location = await getUserLocation();

    const response = await fetch("/api/assistant", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message,
            latitude: userLatitude,
            longitude: userLongitude
        })
    });

    const data = await response.json();

    const aiText = document.createElement("p");
    aiText.textContent = "PhiloShield AI: " + data.reply;
    chatContainer.appendChild(aiText);

    // If PhiloShield returns multiple nearby places
    if (data.places && Array.isArray(data.places)) {
        data.places.forEach((place) => {
            const placeText = document.createElement("p");

            placeText.textContent =
                `${place.number}. 📍 ${place.name} — ` +
                `${place.distance} miles away` +
                (place.address ? ` — Address: ${place.address}` : "");

            chatContainer.appendChild(placeText);

            if (place.directions_url) {
                const placeLink = document.createElement("a");

                placeLink.href = place.directions_url;
                placeLink.target = "_blank";
                placeLink.rel = "noopener noreferrer";
                placeLink.textContent = "🗺️ Get Directions";

                chatContainer.appendChild(placeLink);
            }
        });
    }

    // Normal single-location result
    if (data.directions_url) {
        const directionsLink = document.createElement("a");

        directionsLink.href = data.directions_url;
        directionsLink.target = "_blank";
        directionsLink.rel = "noopener noreferrer";
        directionsLink.textContent = "🗺️ Get Directions";

        chatContainer.appendChild(directionsLink);
    }

});
