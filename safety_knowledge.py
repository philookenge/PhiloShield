SAFETY_KNOWLEDGE = {
    "tornado": (
        "🌪️ TORNADO SAFETY\n\n"
        "• Go to a basement or an interior room on the lowest floor.\n"
        "• Stay away from windows and exterior walls.\n"
        "• Protect your head and neck with your arms, a blanket, "
        "or a sturdy object.\n"
        "• If you are in a mobile home, move to a designated "
        "storm shelter when it is safe to do so.\n"
        "• Continue monitoring official emergency alerts."
    ),

    "fire": (
        "🔥 FIRE SAFETY\n\n"
        "• Leave the building immediately if there is a fire.\n"
        "• Do not stop to collect belongings.\n"
        "• Use stairs instead of elevators.\n"
        "• If there is smoke, stay low while exiting.\n"
        "• Once outside, stay outside and call 911 from a safe place."
    ),

    "flood": (
        "🌊 FLOOD SAFETY\n\n"
        "• Move to higher ground when authorities tell you to evacuate.\n"
        "• Never walk, swim, or drive through floodwater.\n"
        "• Stay away from flooded roads and downed power lines.\n"
        "• Follow evacuation instructions from local authorities."
    ),

    "earthquake": (
        "🏚️ EARTHQUAKE SAFETY\n\n"
        "• Drop to your hands and knees.\n"
        "• Cover your head and neck under a sturdy table if possible.\n"
        "• Hold on until the shaking stops.\n"
        "• Stay away from windows and objects that could fall."
    ),

    "power outage": (
        "🔦 POWER OUTAGE SAFETY\n\n"
        "• Use flashlights instead of candles when possible.\n"
        "• Keep refrigerator and freezer doors closed.\n"
        "• Disconnect sensitive electronics if necessary.\n"
        "• Never operate a generator inside a home or garage.\n"
        "• Follow local emergency information."
    ),

    "emergency kit": (
        "🎒 EMERGENCY KIT\n\n"
        "Consider keeping water, nonperishable food, flashlights, "
        "batteries, a first-aid kit, necessary medications, a phone "
        "charger or power bank, important contact information, and "
        "other supplies appropriate for your household."
    ),

    "earthquake": (
        "🌎 EARTHQUAKE SAFETY\n"
        "• Drop to your hands and knees.\n"
        "• Cover your head and neck under a sturdy table if possible.\n"
        "• Hold on until the shaking stops.\n"
        "• Stay away from windows and objects that may fall.\n"
        "• If outdoors, move away from buildings, trees, and power lines.\n"
        "• After shaking stops, check for hazards and follow official alerts."
    ),

    "thunderstorm": (
        "⛈️ THUNDERSTORM SAFETY\n"
        "• Go indoors when you hear thunder.\n"
        "• Stay away from windows.\n"
        "• Avoid plumbing and electrical equipment during the storm.\n"
        "• If outside, seek a substantial building or enclosed vehicle.\n"
        "• Stay informed through official weather alerts."
    ),

    "extreme heat": (
        "🌡️ EXTREME HEAT SAFETY\n"
        "• Drink plenty of water.\n"
        "• Stay in an air-conditioned or cooler location when possible.\n"
        "• Avoid strenuous outdoor activity during the hottest part of the day.\n"
        "• Never leave children or pets inside a parked vehicle.\n"
        "• Watch for signs of heat exhaustion or heat stroke."
    ),

    "power outage": (
        "🔦 POWER OUTAGE SAFETY\n"
        "• Use flashlights instead of candles when possible.\n"
        "• Keep refrigerators and freezers closed.\n"
        "• Unplug sensitive electronics if necessary.\n"
        "• Never operate a generator indoors or in an attached garage.\n"
        "• Follow information from local authorities and your utility provider."
    ),

    "carbon monoxide": (
        "⚠️ CARBON MONOXIDE SAFETY\n"
        "• If a carbon monoxide alarm sounds, move outside to fresh air.\n"
        "• Call emergency services from a safe location.\n"
        "• Do not re-enter until authorities say it is safe.\n"
        "• Never use generators, grills, or fuel-burning equipment indoors."
    ),

    "evacuation": (
        "🚗 EVACUATION SAFETY\n"
        "• Follow evacuation instructions from local authorities.\n"
        "• Take essential medications, identification, water, and emergency supplies.\n"
        "• Use recommended evacuation routes.\n"
        "• Avoid closed or flooded roads.\n"
        "• Tell family members where you are going when possible."
    ),

    
}


def find_safety_answer(message):
    message = message.lower().strip()

    aliases = {
        "tornado": ["tornado", "twister"],
        "fire": ["fire", "house fire", "building fire"],
        "flood": ["flood", "flooding", "flooded"],
        "earthquake": ["earthquake", "shaking", "ground shaking"],
        "thunderstorm": ["thunderstorm", "thunder", "lightning"],
        "extreme heat": ["extreme heat", "very hot", "heat wave", "heatwave"],
        "power outage": [
            "power outage",
            "electricity went out",
            "no electricity",
            "power went out",
            "blackout"
        ],
        "carbon monoxide": [
            "carbon monoxide",
            "co alarm",
            "carbon monoxide alarm"
        ],
        "evacuation": [
            "evacuation",
            "evacuate",
            "leave my house",
            "leave my home"
        ],
        "emergency kit": [
            "emergency kit",
            "emergency supplies",
            "survival kit"
        ]
    }

    for topic, keywords in aliases.items():
        for keyword in keywords:
            if keyword in message:
                return SAFETY_KNOWLEDGE.get(topic)

    return None
