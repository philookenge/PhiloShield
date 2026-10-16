const notificationSettingsButton =
    document.getElementById("notificationSettingsButton");

notificationSettingsButton.addEventListener("click", async () => {
    const permission = await Notification.requestPermission();

    if (permission === "granted") {
        notificationSettingsButton.textContent = "Notifications Enabled";
    } else {
        notificationSettingsButton.textContent = "Notifications Blocked";
    }
});

if (Notification.permission === "granted") {
    notificationSettingsButton.textContent = "Notifications Enabled";
} else if (Notification.permission === "denied") {
    notificationSettingsButton.textContent = "Notifications Blocked";
}

const locationButton = document.getElementById("locationSettingsButton");

locationButton.addEventListener("click", function () {
    if (!navigator.geolocation) {
        alert("Location is not supported on this device.");
        return;
    }

    locationButton.textContent = "Checking Location...";

    navigator.geolocation.getCurrentPosition(
        function (position) {
            locationButton.textContent = "Location Enabled ✓";
            alert("PhiloShield can access your location.");
        },
        function (error) {
            locationButton.textContent = "Check Location";
            alert("Location access was denied. Please allow location permission.");
        }
    );
});

const darkModeButton = document.getElementById("darkModeButton");

darkModeButton.addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {
        darkModeButton.textContent = "Disable Dark Mode";
    } else {
        darkModeButton.textContent = "Enable Dark Mode";
    }
});
// Save Dark Mode preference
if (localStorage.getItem("philoDarkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    darkModeButton.textContent = "Disable Dark Mode";
}

darkModeButton.addEventListener("click", function () {
    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("philoDarkMode", "enabled");
    } else {
        localStorage.setItem("philoDarkMode", "disabled");
    }
});

// Daily Weather Notifications preference
const dailyWeatherToggle = document.getElementById("dailyWeatherToggle");

if (dailyWeatherToggle) {


    // Save preference when checkbox changes
    dailyWeatherToggle.addEventListener("change", async function () {
        const enabled = dailyWeatherToggle.checked;
        try {
            const response = await fetch("/api/daily-weather-preference", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ enabled: enabled })
            });

            if (!response.ok) {
                dailyWeatherToggle.checked = !enabled;
                alert("Could not save your weather preference. Please try again.");
            }

        } catch (error) {
            dailyWeatherToggle.checked = !enabled;
            console.error("Weather preference save failed:", error);
            alert("Connection error. Could not save your weather preference.");
        }

    });
}