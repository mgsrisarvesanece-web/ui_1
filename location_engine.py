import random

# Sample pseudo crowd data
LOCATIONS = {
    "tirupati temple": {"base": 0.65},
    "sabarimala": {"base": 0.80},
    "marina beach": {"base": 0.30},
    "railway station": {"base": 0.55},
    "airport": {"base": 0.40}
}

def get_location_risk(location_name):
    location = location_name.lower()

    if location in LOCATIONS:
        base = LOCATIONS[location]["base"]
    else:
        base = random.uniform(0.2, 0.6)  # unknown locations

    # add small variation
    sri = round(min(1.0, base + random.uniform(-0.1, 0.1)), 2)

    if sri < 0.4:
        level = "SAFE"
        color = "green"
    elif sri < 0.7:
        level = "CAUTION"
        color = "yellow"
    else:
        level = "DANGER"
        color = "red"

    return {
        "location": location_name.title(),
        "sri": sri,
        "level": level,
        "color": color
    }
