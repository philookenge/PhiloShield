const weatherContainer = document.getElementById("weatherContainer");
const forecastContainer = document.getElementById("forecastContainer");
const hourlyForecastContainer =
    document.getElementById("hourlyForecastContainer");

function loadWeather() {
    weatherContainer.innerHTML =
        "<p>Finding your location...</p>";

    if (!navigator.geolocation) {
        weatherContainer.innerHTML =
            "<p>Your browser does not support location services.</p>";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        fetchWeather,
        showWeatherLocationError
    );
}


async function fetchWeather(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    weatherContainer.innerHTML =
        "<p>Loading current weather...</p>";

    const weatherUrl =
        "https://api.open-meteo.com/v1/forecast" +
        "?latitude=" + latitude +
        "&longitude=" + longitude +
        "&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m" +
        "&hourly=temperature_2m,weather_code,precipitation_probability" +
        "&daily=weather_code,temperature_2m_max,temperature_2m_min," +
        "precipitation_probability_max,sunrise,sunset" +
        "&temperature_unit=fahrenheit" +
        "&wind_speed_unit=mph" +
        "&timezone=auto";

    const airQualityUrl =
        "https://air-quality-api.open-meteo.com/v1/air-quality" +
        "?latitude=" + latitude +
        "&longitude=" + longitude +
        "&current=us_aqi";

    try {
        const [weatherResponse, airQualityResponse] =
            await Promise.all([
                fetch(weatherUrl),
                fetch(airQualityUrl)
            ]);

        if (!weatherResponse.ok) {
            throw new Error("Weather information could not be loaded.");
        }

        if (!airQualityResponse.ok) {
            throw new Error("Air-quality information could not be loaded.");
        }

        const data = await weatherResponse.json();
        const airQualityData = await airQualityResponse.json();

        const weatherCode = data.current.weather_code;
        const condition = getWeatherCondition(weatherCode);

        const aqi = airQualityData.current.us_aqi;
        const airQualityStatus = getAirQualityStatus(aqi);
        const airQualityAdvice = getAirQualityAdvice(aqi);

        weatherContainer.innerHTML =
            "<h2>" + condition + "</h2>" +

            "<p><strong>Temperature:</strong> " +
            data.current.temperature_2m +
            " °F</p>" +

            "<p><strong>Wind speed:</strong> " +
            data.current.wind_speed_10m +
            " mph</p>" +

            "<p><strong>Humidity:</strong> " +
            data.current.relative_humidity_2m +
            "%</p>" +

            "<p><strong>Air Quality:</strong> " +
            airQualityStatus +
            " (" + aqi + ")</p>" +

            "<p><strong>Health Advice:</strong><br>" +
            airQualityAdvice +
            "</p>";
        displayHourlyForecast(data.hourly);
        displayForecast(data.daily);

    } catch (error) {
        console.error(error);

        weatherContainer.innerHTML =
            "<p>Weather information could not be loaded. " +
            "Please try again.</p>";
    }
}


function showWeatherLocationError(error) {
    if (error.code === 1) {
        weatherContainer.innerHTML =
            "<p>Location permission was denied.</p>";
    } else if (error.code === 2) {
        weatherContainer.innerHTML =
            "<p>Your location is unavailable.</p>";
    } else if (error.code === 3) {
        weatherContainer.innerHTML =
            "<p>The location request took too long.</p>";
    } else {
        weatherContainer.innerHTML =
            "<p>Your location could not be determined.</p>";
    }
}


function getWeatherCondition(code) {
    if (code === 0) {
        return "☀️ Clear Sky";
    }

    if (code === 1 || code === 2) {
        return "🌤️ Partly Cloudy";
    }

    if (code === 3) {
        return "☁️ Cloudy";
    }

    if (code === 45 || code === 48) {
        return "🌫️ Foggy";
    }

    if (code >= 51 && code <= 67) {
        return "🌧️ Rain";
    }

    if (code >= 71 && code <= 77) {
        return "❄️ Snow";
    }

    if (code >= 80 && code <= 82) {
        return "🌦️ Rain Showers";
    }

    if (code === 85 || code === 86) {
        return "🌨️ Snow Showers";
    }

    if (code >= 95) {
        return "⛈️ Thunderstorm";
    }

    return "🌤️ Weather Conditions";
}

function displayHourlyForecast(hourly) {
    hourlyForecastContainer.innerHTML =
        "<h2>🕐 48-Hour Forecast</h2>";
    const now = new Date();
    let shown = 0;
    let lastDay = "";

    hourly.time.forEach(function (time, index) {
        const forecastTime = new Date(time);

        if (forecastTime >= now && shown < 48) {
            const dayName =
                forecastTime.toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "short",
                    day: "numeric"
                });

            let dayGroup = document.querySelector(
                '[data-day="' + dayName + '"]'
            );


            if (dayName !== lastDay) {
                const dayHeading = document.createElement("h3");
                dayHeading.className = "hourly-day-heading";
                dayHeading.textContent = dayName;
                hourlyForecastContainer.appendChild(dayHeading);

                dayGroup = document.createElement("div");
                dayGroup.className = "hourly-day-group";
                dayGroup.setAttribute("data-day", dayName);
                hourlyForecastContainer.appendChild(dayGroup);

                lastDay = dayName;
            }
            const hourCard = document.createElement("div");
            hourCard.className = "hourly-weather-row";

            const readableTime =
                forecastTime.toLocaleTimeString("en-US", {
                    hour: "numeric",
                    minute: "2-digit"
                });

            const condition =
                getWeatherCondition(hourly.weather_code[index]);

            hourCard.innerHTML =
                "<strong>" + readableTime + "</strong>" +
                " — " +
                hourly.temperature_2m[index] + " °F" +
                " — " + condition +
                " — 🌧️ " +
                hourly.precipitation_probability[index] + "%";

            dayGroup.appendChild(hourCard);

            shown++;
        }
    });
}


function displayForecast(daily) {
    forecastContainer.innerHTML =
        "<h2>📅 7-Day Forecast</h2>";

    daily.time.forEach(function (date, index) {
        const dayCard = document.createElement("div");

        const readableDate = new Date(
            date + "T12:00:00"
        ).toLocaleDateString("en-US", {
            weekday: "long",
            month: "short",
            day: "numeric"
        });

        const condition =
            getWeatherCondition(daily.weather_code[index]);

        const sunriseTime = new Date(
            daily.sunrise[index]
        ).toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit"
        });

        const sunsetTime = new Date(
            daily.sunset[index]
        ).toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit"
        });

        dayCard.innerHTML =
            "<h3>" + readableDate + "</h3>" +
            "<p>" + condition + "</p>" +

            "<p><strong>High:</strong> " +
            daily.temperature_2m_max[index] +
            " °F</p>" +

            "<p><strong>Low:</strong> " +
            daily.temperature_2m_min[index] +
            " °F</p>" +

            "<p><strong>Chance of rain:</strong> " +
            daily.precipitation_probability_max[index] +
            "%</p>" +

            "<p><strong>Sunrise:</strong> " +
            sunriseTime +
            "</p>" +

            "<p><strong>Sunset:</strong> " +
            sunsetTime +
            "</p>";

        forecastContainer.appendChild(dayCard);
    });
}


function getAirQualityStatus(aqi) {
    if (aqi <= 50) {
        return "🌿 Good";
    }

    if (aqi <= 100) {
        return "🟡 Moderate";
    }

    if (aqi <= 150) {
        return "🟠 Unhealthy for sensitive groups";
    }

    if (aqi <= 200) {
        return "🔴 Unhealthy";
    }

    if (aqi <= 300) {
        return "🟣 Very Unhealthy";
    }

    return "🟤 Hazardous";
}


function getAirQualityAdvice(aqi) {
    if (aqi <= 50) {
        return "😊 Air quality is excellent. " +
            "Outdoor activities are safe for everyone.";
    }

    if (aqi <= 100) {
        return "🙂 Air quality is acceptable. " +
            "Most people can enjoy outdoor activities.";
    }

    if (aqi <= 150) {
        return "😷 Sensitive people should reduce " +
            "prolonged outdoor activities.";
    }

    if (aqi <= 200) {
        return "⚠️ Everyone should limit prolonged " +
            "outdoor activities.";
    }

    if (aqi <= 300) {
        return "🚨 Avoid outdoor activities if possible.";
    }

    return "☣️ Stay indoors and follow local health advisories.";
}


loadWeather();
