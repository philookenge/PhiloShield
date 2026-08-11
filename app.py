from flask import Flask, render_template, jsonify, request, send_from_directory
import requests

app = Flask(__name__)


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

        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": overpass_query},
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        map_data = response.json()

        nearby_places = []

        for element in map_data.get("elements", []):
            tags = element.get("tags", {})
            place_type = tags.get("amenity") or tags.get("healthcare")

            if not place_type:
                continue

            place_latitude = element.get("lat")
            place_longitude = element.get("lon")

            if place_latitude is None or place_longitude is None:
                center = element.get("center", {})
                place_latitude = center.get("lat")
                place_longitude = center.get("lon")

            if place_latitude is None or place_longitude is None:
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

        return jsonify(nearby_places)

    except requests.RequestException as error:
        print("OVERPASS ERROR DETAILS:")
        print(repr(error))

        return jsonify({
            "error": "Nearby emergency resources could not be loaded."
        }), 503

@app.route("/api/alerts")
def emergency_alerts():
    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("lon", type=float)

    if latitude is None or longitude is None:
        return jsonify({
            "error": "Latitude and longitude are required."
        }), 400

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

        return jsonify(alerts)

    except requests.RequestException as error:
        print("NWS ALERT API ERROR:")
        print(repr(error))

        return jsonify({
            "error": "Official emergency alerts could not be loaded."
        }), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)