from email.mime import message

from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import json
import os
import threading
import time
from pywebpush import webpush, WebPushException
from datetime import datetime, timedelta
from openai import OpenAI
from safety_knowledge import find_safety_answer

app = Flask(__name__)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"]) if os.environ.get("OPENAI_API_KEY") else None

VAPID_PRIVATE_KEY = os.path.join(
    os.path.dirname(__file__),
    "private_key.pem"
)

VAPID_CLAIMS = {
    "sub": "mailto:philookenge37@gmail.com"
}

SUBSCRIPTIONS_FILE = os.path.join(
    os.path.dirname(__file__),
    "subscriptions.json"
)

ALERT_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "alert_history.json"
)

LAST_LOCATION_FILE = os.path.join(
    os.path.dirname(__file__),
    "last_location.json"
)

DAILY_WEATHER_PREFERENCE_FILE = os.path.join(
    os.path.dirname(__file__),
    "daily_weather_preference.json"
)

PLACES_CACHE_FILE = os.path.join(
    os.path.dirname(__file__),
    "places_cache.json"
)


PLACES_CACHE = {}
PLACES_CACHE_DURATION = timedelta(hours=24)

def load_places_cache_file():
    if not os.path.exists(PLACES_CACHE_FILE):
        return None

    try:
        with open(PLACES_CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None


def save_places_cache_file(cache_key, nearby_places):
    try:
        with open(PLACES_CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump({
                "lat": cache_key[0],
                "lon": cache_key[1],
                "timestamp": datetime.now().isoformat(),
                "places": nearby_places
            }, file, indent=2)

    except OSError as error:
        print("Could not save places cache:", error)


def load_subscriptions():
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return []

    try:
        with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_subscriptions(subscriptions):
    with open(SUBSCRIPTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(subscriptions, file, indent=2)

def save_last_location(latitude, longitude):
    data = {
        "lat": latitude,
        "lon": longitude
    }

    with open(LAST_LOCATION_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

def save_daily_weather_preference(enabled):
    with open(DAILY_WEATHER_PREFERENCE_FILE, "w", encoding="utf-8") as file:
        json.dump({"enabled": enabled}, file, indent=2)

def load_daily_weather_preference():
    if not os.path.exists(DAILY_WEATHER_PREFERENCE_FILE):
        return True 
    try:
        with open(DAILY_WEATHER_PREFERENCE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("enabled", True)
    except (json.JSONDecodeError, OSError):
        return True
    
def load_last_location():
    if not os.path.exists(LAST_LOCATION_FILE):
        return None

    try:
        with open(LAST_LOCATION_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None

def automatic_alert_checker():
    while True:
        try:
            location = load_last_location()

            if location:
                latitude = location.get("lat")
                longitude = location.get("lon")

                if latitude is not None and longitude is not None:
                    api_url = (
                        "https://api.weather.gov/alerts/active"
                        f"?point={latitude},{longitude}"
                    )

                    headers = {
                        "User-Agent": (
                            "PhiloShield-Emergency-App/1.0 "
                            "(contact: philookenge37@gmail.com)"
                        ),
                        "Accept": "application/geo+json"
                    }

                    response = requests.get(
                        api_url,
                        headers=headers,
                        timeout=10
                    )

                    response.raise_for_status()
                    weather_data = response.json()

                    alerts = []

                    for feature in weather_data.get("features", []):
                        properties = feature.get("properties", {})

                        alerts.append({
                            "id": feature.get("id"),
                            "event": properties.get(
                                "event",
                                "Emergency Alert"
                            ),
                            "headline": properties.get(
                                "headline",
                                "No headline available."
                            )
                        })

                    if alerts:
                        alert_history = load_alert_history()
                        first_alert = alerts[0]
                        alert_id = first_alert.get("id")

                        if alert_id and alert_id not in alert_history:
                            send_push_message(
                                first_alert.get(
                                    "event",
                                    "PhiloShield Emergency Alert"
                                ),
                                first_alert.get(
                                    "headline",
                                    "An official emergency alert is active."
                                )
                            )

                            alert_history.append(alert_id)
                            save_alert_history(alert_history)

        except Exception as error:
            print(
                "Automatic alert checker error:",
                error
            )

        time.sleep(300)

last_weather_check_notification_date = None       

def daily_weather_checker():
    global last_weather_check_notification_date
    while True:
        try:
            now = datetime.now()

            if now.hour == 7 and now.minute == 0 and last_weather_check_notification_date != now.date():

                                                  if not load_daily_weather_preference():
                                                        time.sleep(60)
                                                        continue

                                                  location = load_last_location()
                                                  if location:
                                                      latitude = location.get("lat")
                                                      longitude = location.get("lon")

                                                      if latitude is not None and longitude is not None:
                                                          weather_description = get_current_weather(latitude, longitude)

                                                          if weather_description:
                                                              safety_advice = get_weather_safety_advice(weather_description)
                                                              send_daily_weather_notification(weather_description, safety_advice)
                                                              send_daily_weather_notification(weather_description, safety_advice)
                                                              last_weather_check_notification_date = now.date()
        except Exception as error:
            print("Daily weather checker error:", error)

        time.sleep(60)

@app.route("/api/weather-preference", methods=["POST"])
def weather_preference():
    data = request.get_json()
    enabled = data.get("enabled", True)
    save_daily_weather_preference(enabled)

    return jsonify({
        "success": True,
        "enabled": enabled
    })

@app.route("/subscribe", methods=["POST"])
def subscribe():
    subscription = request.get_json()

    if not subscription:
        return jsonify({
            "success": False,
            "message": "No subscription received."
        }), 400

    subscriptions = load_subscriptions()

    # Avoid saving the same browser subscription multiple times
    endpoint = subscription.get("endpoint")

    already_saved = any(
        saved.get("endpoint") == endpoint
        for saved in subscriptions
    )

    if not already_saved:
        subscriptions.append(subscription)
        save_subscriptions(subscriptions)

    print(
        f"Subscription saved. Total subscriptions: "
        f"{len(subscriptions)}"
    )

    return jsonify({
        "success": True,
        "message": "PhiloShield push subscription saved.",
        "subscriptions": len(subscriptions)
    })
def send_push_message(title, body):
    subscriptions = load_subscriptions()

    if not subscriptions:
        return 0

    payload = json.dumps({
        "title": title,
        "body": body
    })

    sent = 0
    valid_subscriptions = []

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS,
                headers={
                    "X-WNS-Type": "wns/raw"
                }
            )

            sent += 1
            valid_subscriptions.append(subscription)

        except WebPushException as error:
            print("Push notification error:", error)

            if error.response is not None:
                if error.response.status_code not in (404, 410):
                    valid_subscriptions.append(subscription)
            else:
                valid_subscriptions.append(subscription)

    save_subscriptions(valid_subscriptions)

    return sent

def send_daily_weather_notification(weather_description, safety_advice):
    title = "🌤️ PhiloShield Daily Weather"

    body = (
        f"Today's weather: {weather_description}\n"
        f"🛡️ Safety Tip: {safety_advice}"
    )

    return send_push_message(title, body)

def get_weather_safety_advice(weather_description):
    weather = weather_description.lower()

    if "thunder" in weather or "storm" in weather:
        return "Stay indoors and away from windows during thunderstorms."

    if "snow" in weather or "ice" in weather:
        return "Dress warmly and be careful on slippery roads and sidewalks."

    if "rain" in weather:
        return "Carry an umbrella and use extra caution while driving."

    if "hot" in weather or "heat" in weather:
        return "Drink plenty of water and avoid staying in direct sun too long."

    if "cold" in weather or "freezing" in weather:
        return "Wear warm layers and limit time outdoors."

    if "fog" in weather:
        return "Drive slowly and use low-beam headlights."

    return "Check conditions before going out and stay prepared."



@app.route("/send-notification", methods=["POST"])
def send_notification():
    subscriptions = load_subscriptions()

    print(
        f"Trying to send notification to "
        f"{len(subscriptions)} subscription(s)."
    )

    if not subscriptions:
        return jsonify({
            "success": False,
            "message": "No devices are subscribed yet."
        }), 400

    payload = json.dumps({
        "title": "PhiloShield Emergency Alert",
        "body": (
            "This is a test emergency notification "
            "from PhiloShield."
        )
    })

    sent = 0
    valid_subscriptions = []

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS,
                headers={
                    "X-WNS-Type": "wns/raw"
                }
            )

            sent += 1
            valid_subscriptions.append(subscription)

        except WebPushException as error:
            print("Push notification error:", error)

            if error.response is not None:
                print(
                    "Status code:",
                    error.response.status_code
                )

                try:
                    print(
                        "Response body:",
                        error.response.text
                    )
                except Exception:
                    pass

                if error.response.status_code not in (404, 410):
                    valid_subscriptions.append(subscription)

            else:
                valid_subscriptions.append(subscription)

    save_subscriptions(valid_subscriptions)

    return jsonify({
        "success": sent > 0,
        "message": f"Notification sent to {sent} device(s).",
        "sent": sent,
        "subscriptions": len(valid_subscriptions)
    })

def load_alert_history():
    if not os.path.exists(ALERT_HISTORY_FILE):
        return []

    try:
        with open(ALERT_HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_alert_history(history):
    with open(ALERT_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)

def get_current_weather(latitude, longitude):
    if latitude is None or longitude is None:
        return None

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        temperature = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code")

        conditions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Cloudy",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Heavy drizzle",
            61: "Light rain",
            63: "Rain",
            65: "Heavy rain",
            71: "Light snow",
            73: "Snow",
            75: "Heavy snow",
            80: "Rain showers",
            81: "Rain showers",
            82: "Heavy rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with hail"
        }

        condition = conditions.get(code, "Current conditions")

        safety_advice = get_weather_safety_advice(condition)

        return (
            f"🌤️ CURRENT WEATHER\n"
            f"• Condition: {condition}\n"
            f"• Temperature: {temperature}°F\n"
            f"• Humidity: {humidity}%\n"
            f"• Wind: {wind} mph\n"
            f"🛡️ Safety Tip: {safety_advice}"

        )

    except requests.RequestException:
        return None


@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    data = request.get_json()
    message = data.get("message", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    from datetime import datetime

    time_words = [
        "what time is it",
        "current time",
        "time now"
    ]

    date_words = [
        "what date is it",
        "what day is today",
        "what day is it",
        "today's date",
        "current date"
    ]

    message_lower = message.lower()

    if any(word in message_lower for word in time_words):
        now = datetime.now()
        return jsonify({
            "reply": f"🕐 The current time is {now.strftime('%I:%M %p')}."
        })

    if any(word in message_lower for word in date_words):
        now = datetime.now()
        return jsonify({
            "reply": f"📅 Today is {now.strftime('%A, %B %d, %Y')}."
        })
    
    # Nearby emergency places
    nearby_words = [
    "hospital",
    "medical center",
    "emergency room",
    "er near",
    "police",
    "police station",
    "police department",
    "cop",
    "cops",
    "officer",
    "law enforcement",
    "sheriff",
    "fire station",
    "fire department",
    "firefighter"
]

    if any(word in message_lower for word in nearby_words):
        if latitude is None or longitude is None:
            return jsonify({
                "reply": "📍 I need your location to find nearby emergency places. Please allow location access."
            })


                # Use the nearby places already saved by the Safe Places map
        try:
            cache_data = load_places_cache_file()

            if not cache_data:
                return jsonify({
                    "reply": (
                        "📍 I don't have nearby emergency places saved yet. "
                        "Please open Nearby Safe Places once, then try again."
                    )
                })

            nearby_places = cache_data.get("places", [])

            if not nearby_places:
                return jsonify({
                    "reply": "📍 I couldn't find any saved emergency places nearby."
                })

            # Determine what type of place the user requested
            if "hospital" in message_lower:
                wanted_type = "hospital"
            elif any(word in message_lower for word in ["police", "cop", "sheriff"]):
                wanted_type = "police"
            elif "fire" in message_lower:
                wanted_type = "fire_station"
            else:
                wanted_type = None

            matching_places = [
                place for place in nearby_places
                if wanted_type is None
                or place.get("type") == wanted_type
            ]

            if not matching_places:
                return jsonify({
                    "reply": "📍 I couldn't find that type of emergency place nearby."
                })

         # Calculate distance from the user's current location
            for place in matching_places:
                place_lat = place.get("lat")
                place_lon = place.get("lon")

                if place_lat is not None and place_lon is not None:
                    place["distance"] = haversine_distance(
                        latitude,
                        longitude,
                        place_lat,
                        place_lon
                    )
                else:
                    place["distance"] = float("inf")

                        # Sort places from closest to farthest
            sorted_places = sorted(
                matching_places,
                key=lambda place: place["distance"]
            )

            # Keep the closest place for normal "nearest" questions
            nearest = sorted_places[0]

            # Keep up to 3 places for "3 nearest" questions
            three_nearest = sorted_places[:3]

            # Check if the user is asking for the 3 nearest places
            wants_three = any(phrase in message_lower for phrase in [
                "3 nearest",
                "three nearest",
                "3 closest",
                "three closest"
])

            if wants_three:
                results = []

                for index, place in enumerate(three_nearest, start=1):
                    place_name = place.get("name", "Emergency location")
                    place_distance = place.get("distance", "unknown")
                    place_address = place.get("address", "")
                    place_lat = place.get("lat")
                    place_lon = place.get("lon")

                    item = {
                        "number": index,
                        "name": place_name,
                        "distance": place_distance,
                        "address": place_address
                    }

                    if place_lat is not None and place_lon is not None:
                        item["directions_url"] = (
                            "https://www.google.com/maps/dir/?api=1"
                            f"&destination={place_lat},{place_lon}"
                        )

                    results.append(item)

                return jsonify({
                    "reply": "Here are the 3 nearest emergency places:",
                    "places": results
                })

        
            name = nearest.get(
                "name",
                "Emergency location"
            )

            distance = nearest.get("distance")
            address = nearest.get("address", "")

            place_lat = nearest.get("lat")
            place_lon = nearest.get("lon")

            reply = (
                f"📍 The nearest is {name}, "
                f"about {distance} miles away."
            )

            if address:
                reply += f" Address: {address}."

            if place_lat is not None and place_lon is not None:
             directions_url = (
                f"https://www.google.com/maps/dir/?api=1"
                f"&destination={place_lat},{place_lon}"
            )

           

            return jsonify({
    "reply": reply,
    "directions_url": directions_url if place_lat is not None and place_lon is not None else None
})


        except Exception as error:
            print(
                "NEARBY ASSISTANT ERROR:",
                repr(error)
            )

            return jsonify({
                "reply": (
                    "📍 I couldn't read the saved nearby "
                    "emergency places."
                )
            })


        
    # Check PhiloShield's free built-in safety knowledge first
    safety_answer = find_safety_answer(message)

    if safety_answer:
        return jsonify({"reply": safety_answer})

    # Current date and day
    date_words = [
        "what date is it",
        "what is the date",
        "what's the date",
        "today's date",
        "what day is it",
        "what day is today",
        "what is today",
        "date today"
    ]

    if any(word in message.lower() for word in date_words):
        now = datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")

        return jsonify({
            "reply": f"📅 Today is {current_date}."
        })

    # Emergency phone numbers - United States
    emergency_number_words = [
        "emergency number",
        "emergency phone number",
        "who do i call in an emergency",
        "who should i call in an emergency",
        "someone is in danger",
        "call police",
        "call an ambulance",
        "call firefighters",
        "poison control",
        "poison number",
        "what number should i call in an emergency",
        "what number do i call in an emergency",
        "what number to call in an emergency",
        "what should i call in an emergency"
    ]

    if any(
        word in message.lower()
        for word in emergency_number_words
    ):
        if "poison" in message.lower():
            return jsonify({
                "reply": (
                    "☠️ U.S. Poison Control: 1-800-222-1222. "
                    "If the person is unconscious, having trouble "
                    "breathing, having a seizure, or is in immediate "
                    "danger, call 911."
                )
            })

        return jsonify({
            "reply": (
                "🚨 In the United States, call 911 for an immediate "
                "police, fire, or medical emergency. "
                "If you are outside the United States, use your "
                "country's local emergency number."
            )
        })

    # Current weather
    weather_words = [
        "weather",
        "temperature",
        "temperature outside",
        "weather now",
        "how hot",
        "how cold"
    ]

    if any(word in message.lower() for word in weather_words):
        if latitude is None or longitude is None:
            return jsonify({
                "reply": (
                    "📍 I need your location to check the current "
                    "weather. Please allow location access."
                )
            })

        weather_answer = get_current_weather(
            latitude,
            longitude
        )

        if weather_answer:
            return jsonify({"reply": weather_answer})

        return jsonify({
            "reply": (
                "I couldn't load the current weather right now. "
                "Please try again."
            )
        })

    # Free PhiloShield assistant fallback
    return jsonify({
        "reply": (
            "I don't have a specific answer to that question yet. "
            "I can help with emergency preparedness, weather safety, "
            "first aid basics, evacuation, shelters, and emergency kits. "
            "Please try asking about one of these topics."
        )
    })


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shelter")
def shelter():
    return render_template("shelter_map.html")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(
        "static",
        "service-worker.js",
        mimetype="application/javascript"
    )


@app.route("/alerts")
def alerts():
    return render_template("alerts.html")


@app.route("/kit")
def kit():
    return render_template("kit.html")


@app.route("/family")
def family():
    return render_template("family.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/weather")
def weather():
    return render_template("weather.html")


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/settings")
def settings():
    daily_weather_enabled = load_daily_weather_preference()
    return render_template(
        "settings.html",
        daily_weather_enabled=daily_weather_enabled
    )

@app.route("/api/daily-weather-preference", methods=["POST"])
def update_daily_weather_preference():
    data = request.get_json(silent=True) or {}

    enabled = data.get("enabled")

    if not isinstance(enabled, bool):
        return jsonify({"error": "Invalid preference"}), 400

    save_daily_weather_preference(enabled)

    return jsonify({
        "success": True,
        "enabled": enabled
    })


@app.route("/sos")
def sos():
    return render_template("sos.html")


@app.route("/firstaid")
def firstaid():
    return render_template("firstaid.html")


@app.route("/flashlight")
def flashlight():
    return render_template("flashlight.html")


@app.route("/medicalid")
def medicalid():
    return render_template("medicalid.html")


@app.route("/share")
def share():
    return render_template("share.html")


@app.route("/share-app")
def share_app():
    return render_template("share_app.html")


@app.route("/offline")
def offline():
    return render_template("offline.html")


def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    earth_radius = 3958.8

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return round(earth_radius * c, 2)


@app.route("/api/places")
def places():
    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("lon", type=float)

    if latitude is None or longitude is None:
        return jsonify({
            "error": "Latitude and longitude are required."
        }), 400

    cache_key = (
        round(latitude, 2),
        round(longitude, 2)
    )

    cached = PLACES_CACHE.get(cache_key)

    if (
        cached
        and datetime.now() - cached["timestamp"]
        < PLACES_CACHE_DURATION
    ):
        print("Using cached nearby places.")
        return jsonify(cached["places"])

    file_cache = load_places_cache_file()

    if file_cache:
        try:
            file_key = (
                round(float(file_cache["lat"]), 2),
                round(float(file_cache["lon"]), 2)
            )

            if file_key == cache_key:
                file_timestamp = datetime.fromisoformat(
                    file_cache["timestamp"]
                )

                cached = {
                    "timestamp": file_timestamp,
                    "places": file_cache["places"]
                }

                PLACES_CACHE[cache_key] = cached

                if (
                    datetime.now() - file_timestamp
                    < PLACES_CACHE_DURATION
                ):
                    print("Using saved nearby places cache.")
                    return jsonify(file_cache["places"])

        except (KeyError, ValueError, TypeError):
            pass

    overpass_query = f"""
    [out:json][timeout:25];
    (
        node["amenity"="hospital"](around:10000,{latitude},{longitude});
        way["amenity"="hospital"](around:10000,{latitude},{longitude});
        relation["amenity"="hospital"](around:10000,{latitude},{longitude});

        node["healthcare"="hospital"](around:10000,{latitude},{longitude});
        way["healthcare"="hospital"](around:10000,{latitude},{longitude});
        relation["healthcare"="hospital"](around:10000,{latitude},{longitude});

        node["amenity"="fire_station"](around:8000,{latitude},{longitude});
        way["amenity"="fire_station"](around:8000,{latitude},{longitude});
        relation["amenity"="fire_station"](around:8000,{latitude},{longitude});

        node["amenity"="police"](around:8000,{latitude},{longitude});
        way["amenity"="police"](around:8000,{latitude},{longitude});
        relation["amenity"="police"](around:8000,{latitude},{longitude});
    );
    out center;
    """

    try:
        headers = {
            "User-Agent": "SafeShield-Emergency-App/1.0",
            "Accept": "application/json"
        }

        overpass_servers = [
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass-api.de/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"
        ]

        map_data = None
        last_error = None

        for server_url in overpass_servers:
            try:
                response = requests.post(
                    server_url,
                    data={"data": overpass_query},
                    headers=headers,
                    timeout=8
                )

                response.raise_for_status()
                map_data = response.json()
                break

            except requests.RequestException as error:
                print(
                    f"Overpass server failed: {server_url}"
                )
                print(repr(error))
                last_error = error

        if map_data is None:
            raise requests.RequestException(
                f"All Overpass servers failed: {last_error}"
            )

        nearby_places = []

        for element in map_data.get("elements", []):
            tags = element.get("tags", {})

            place_type = (
                tags.get("amenity")
                or tags.get("healthcare")
            )

            if not place_type:
                continue

            place_latitude = element.get("lat")
            place_longitude = element.get("lon")

            if (
                place_latitude is None
                or place_longitude is None
            ):
                center = element.get("center", {})
                place_latitude = center.get("lat")
                place_longitude = center.get("lon")

            if (
                place_latitude is None
                or place_longitude is None
            ):
                continue

            address_parts = [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:city"),
                tags.get("addr:state"),
                tags.get("addr:postcode")
            ]

            address = ", ".join(
                part for part in address_parts if part
            )

            nearby_places.append({
                "name": tags.get(
                    "name",
                    place_type.replace("_", " ").title()
                ),
                "lat": place_latitude,
                "lon": place_longitude,
                "distance": haversine_distance(
                    latitude,
                    longitude,
                    place_latitude,
                    place_longitude
                ),
                "type": place_type,
                "phone": (
                    tags.get("phone")
                    or tags.get("contact:phone")
                ),
                "website": (
                    tags.get("website")
                    or tags.get("contact:website")
                ),
                "address": address
            })

        PLACES_CACHE[cache_key] = {
            "timestamp": datetime.now(),
            "places": nearby_places
        }

        save_places_cache_file(
            cache_key,
            nearby_places
        )

        return jsonify(nearby_places)

    except requests.RequestException as error:
        print("OVERPASS ERROR DETAILS:")
        print(repr(error))

        if cached:
            print(
                "Overpass failed. "
                "Using older cached nearby places."
            )
            return jsonify(cached["places"])

        return jsonify({
            "error": (
                "Nearby emergency resources "
                "could not be loaded."
            )
        }), 503


@app.route("/api/alerts")
def emergency_alerts():
    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("lon", type=float)

    if latitude is None or longitude is None:
        return jsonify({
            "error": "Latitude and longitude are required."
        }), 400

    save_last_location(latitude, longitude)

    api_url = (
        "https://api.weather.gov/alerts/active"
        f"?point={latitude},{longitude}"
    )

    headers = {
        "User-Agent": (
            "SafeShield-Emergency-App/1.0 "
            "(contact: your-email@example.com)"
        ),
        "Accept": "application/geo+json"
    }

    try:
        response = requests.get(
            api_url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()
        weather_data = response.json()

        alerts = []

        for feature in weather_data.get("features", []):
            properties = feature.get("properties", {})

            alerts.append({
                "id": feature.get("id"),
                "event": properties.get(
                    "event",
                    "Emergency Alert"
                ),
                "severity": properties.get(
                    "severity",
                    "Unknown"
                ),
                "area": properties.get(
                    "areaDesc",
                    "Area unavailable"
                ),
                "headline": properties.get(
                    "headline",
                    "No headline available."
                ),
                "instruction": (
                    properties.get("instruction")
                    or "Follow instructions from local authorities."
                )
            })

        if alerts:
            alert_history = load_alert_history()
            first_alert = alerts[0]
            alert_id = first_alert.get("id")

            if alert_id and alert_id not in alert_history:
                send_push_message(
                    first_alert.get(
                        "event",
                        "PhiloShield Emergency Alert"
                    ),
                    first_alert.get(
                        "headline",
                        "An official emergency alert is active."
                    )
                )

                alert_history.append(alert_id)
                save_alert_history(alert_history)

        return jsonify(alerts)

    except requests.RequestException as error:
        print("NWS ALERT API ERROR:")
        print(repr(error))

        return jsonify({
            "error": (
                "Official emergency alerts "
                "could not be loaded."
            )
        }), 503


if __name__ == "__main__":
    alert_thread = threading.Thread(
        target=automatic_alert_checker,
        daemon=True
    )
    alert_thread.start()

    weather_thread = threading.Thread(
        target=daily_weather_checker,
        daemon=True
    )
    weather_thread.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
