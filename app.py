from flask import Flask, request, jsonify, send_from_directory
from ics import Calendar, Event
from datetime import datetime
import pytz
import os
import uuid

app = Flask(__name__)
ics_dir = "ics_files"
os.makedirs(ics_dir, exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate_ics():
    data = request.json
    tz_name = data.get("timezone", "UTC")  # Default to UTC if not specified
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return jsonify({"error": "Invalid timezone"}), 400

    try:
        # Parse ISO 8601 strings and apply timezone
        start = tz.localize(datetime.fromisoformat(data["startTime"]))
        end = tz.localize(datetime.fromisoformat(data["endTime"]))
    except Exception as e:
        return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400

    event = Event()
    event.name = data.get("title", "Untitled Event")
    event.begin = start
    event.end = end
    event.description = data.get("description", "")
    event.location = data.get("location", "")

    cal = Calendar()
    cal.events.add(event)

    uid = str(uuid.uuid4())
    filename = f"{uid}.ics"
    filepath = os.path.join(ics_dir, filename)

    with open(filepath, "w") as f:
        f.writelines(cal)

    download_url = request.url_root.rstrip("/") + f"/ics/{filename}"
    return jsonify({"downloadUrl": download_url})
