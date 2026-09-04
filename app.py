from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import json
import os
import threading
import time
from pywebpush import webpush, WebPushException
from datetime import datetime, timedelta

app = Flask(__name__)

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


@app.route("/offline")
def offline():
    return render_template("offline.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")


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

    # Check memory cache first
    cached = PLACES_CACHE.get(cache_key)

    if (
        cached
        and datetime.now() - cached["timestamp"]
        < PLACES_CACHE_DURATION
    ):
        print("Using cached nearby places.")
        return jsonify(cached["places"])

    # Check saved file cache
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
            "https://overpass.nchc.org.tw/api/interpreter",
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

        # Save successful result in memory
        PLACES_CACHE[cache_key] = {
            "timestamp": datetime.now(),
            "places": nearby_places
        }

        # Save successful result in places_cache.json
        save_places_cache_file(
            cache_key,
            nearby_places
        )

        return jsonify(nearby_places)

    except requests.RequestException as error:
        print("OVERPASS ERROR DETAILS:")
        print(repr(error))

        # Use older cache if Overpass is unavailable
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
                "instruction": properties.get(
                    "instruction"
                ) or "Follow instructions from local authorities."
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
            "error": "Official emergency alerts could not be loaded."
        }), 503


if __name__ == "__main__":
    alert_thread = threading.Thread(
        target=automatic_alert_checker,
        daemon=True
    )
    alert_thread.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )


