import os
import csv
import requests
from datetime import datetime
from flask import Flask, render_template, Response, redirect, request, session, jsonify
from dotenv import load_dotenv
from camera_worker import CameraWorker, camera_frames
from location_engine import get_location_risk

# ================= LOAD ENV =================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ================= APP =================

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ================= USERS =================

USERS = {
    "authority": {"password": "admin123", "role": "authority"},
    "user": {"password": "1234", "role": "user"}
}

# ================= CAMERA =================

camera_sources = {"CAM1": 1}   # you can add more cameras here later
workers = []

for cam_id, source in camera_sources.items():
    worker = CameraWorker(cam_id, source)
    worker.start()
    workers.append(worker)

# ================= LOG FILE =================

LOG_FILE = "alerts_log.csv"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Camera", "Message"])

# ================= TELEGRAM =================

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=payload, timeout=5)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram error:", e)

# ================= LOGIN =================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS and USERS[username]["password"] == password:
            session["role"] = USERS[username]["role"]
            if session["role"] == "authority":
                return redirect("/authority")
            else:
                return redirect("/user")

    return render_template("login.html")

# ================= DASHBOARDS =================

@app.route("/authority")
def authority_dashboard():
    if session.get("role") != "authority":
        return redirect("/")
    return render_template("dashboard.html")

@app.route("/user")
def user_dashboard():
    if session.get("role") != "user":
        return redirect("/")
    return render_template("user_dashboard.html")

# ================= SEARCH ROUTE (FIXED) =================

@app.route("/search", methods=["GET"])
def search_location():
    if session.get("role") != "user":
        return redirect("/")

    location = request.args.get("location", "").strip()

    if not location:
        return render_template("user_dashboard.html")

    result = get_location_risk(location)

    return render_template(
        "search_result.html",
        location=result["location"],
        risk=result["level"]   # SAFE / CAUTION / DANGER
    )

# ================= MANUAL ALERT =================

@app.route("/manual_alert", methods=["POST"])
def manual_alert():
    if session.get("role") != "authority":
        return jsonify({"status": "unauthorized"}), 403

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = "MANUAL ALERT TRIGGERED - HIGH RISK"

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, "CAM1", message])

    send_telegram(f"PRISM SAFE ALERT\nTime: {timestamp}\nCamera: CAM1\nStatus: MANUAL ALERT")

    return jsonify({"status": "success"})

# ================= ALERTS PAGE =================

@app.route("/alerts")
def alerts_page():
    if session.get("role") != "authority":
        return redirect("/")
    return render_template("alerts.html")

# ================= LOGS PAGE =================

@app.route("/logs")
def logs_page():
    if session.get("role") != "authority":
        return redirect("/")
    return render_template("logs.html")

# ================= SETTINGS =================

@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    if session.get("role") != "authority":
        return redirect("/")
    # You can add POST handling later if needed
    return render_template(
        "settings.html",
        bot_token=BOT_TOKEN or "",
        chat_id=CHAT_ID or ""
    )

# ================= API ROUTES =================

@app.route("/api/alerts")
def api_alerts():
    data = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        pass
    return jsonify(data[::-1])  # newest first

@app.route("/api/logs")
def api_logs():
    # Note: currently same file as alerts — you might want separate logs later
    return api_alerts()  # reuse for now

# ================= VIDEO STREAM =================

def generate(camera_id):
    while True:
        if camera_id in camera_frames:
            frame = camera_frames[camera_id]
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/video/<camera_id>")
def video(camera_id):
    return Response(generate(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ================= LOGOUT =================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
    # debug=False → better for camera streaming
    # host=0.0.0.0 → accessible from local network if needed