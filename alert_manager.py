from datetime import datetime

MAX_ALERTS = 50
alerts = []

def classify_level(sri):
    if sri < 0.30:
        return "SAFE"
    elif sri < 0.55:
        return "CAUTION"
    elif sri < 0.75:
        return "HIGH"
    else:
        return "CRITICAL"

def recommended_action(level):
    actions = {
        "SAFE": "No action required",
        "CAUTION": "Monitor situation",
        "HIGH": "Deploy staff to regulate crowd",
        "CRITICAL": "Initiate emergency crowd control protocol"
    }
    return actions.get(level, "Monitor")

def add_alert(camera_id, sri_left, sri_right):
    max_sri = max(sri_left, sri_right)
    level = classify_level(max_sri)

    if level in ["HIGH", "CRITICAL"]:
        alert = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "camera": camera_id,
            "level": level,
            "sri_value": round(max_sri, 2),
            "action": recommended_action(level)
        }

        alerts.append(alert)

        if len(alerts) > MAX_ALERTS:
            alerts.pop(0)

def get_alerts():
    return alerts[::-1]  # newest first
