import requests
from datetime import datetime

BOT_TOKEN = "YOUR_NEW_TOKEN_AFTER_REVOKE"
CHAT_IDS = ["1558332686"]

def send_telegram_alert(location, level):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = f"""
🚨 PRISM SAFE LIVE ALERT 🚨

📍 Source: {location}
⚠ Risk Level: {level}
🕒 Time: {timestamp}

Live crowd threshold exceeded.
"""

    for chat_id in CHAT_IDS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }

        try:
            requests.post(url, data=payload, timeout=5)
        except:
            print("Telegram send failed")
