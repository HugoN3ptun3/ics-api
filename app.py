from flask import Flask, request, jsonify, send_from_directory
from ics import Calendar, Event
from datetime import datetime
import pytz
import os
import uuid

app = Flask(__name__)

# Directory to save .ics files
ics_dir = "ics_files"
os.makedirs(ics_dir, exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate_bulk_ics():
    data = request.json
    tz_name = data.get("timezone", "UTC")
    
    # Validate timezone
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return jsonify({"error": "Invalid timezone"}), 400

    events_data = data.get("events", [])
    if not events_data:
        return jsonify({"error": "No events provided"}), 400

    cal = Calendar()

    for item in events_data:
        try:
            # Localize event times to user timezone
            start = tz.localize(datetime.fromisoformat(item["startTime"]))
            end = tz.localize(datetime.fromisoformat(item["endTime"]))
        except Exception as e:
            return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400

        # Create calendar event
        event = Event()
        event.name = item.get("title", "Untitled Event")
        event.begin = start
        event.end = end
        event.description = item.get("description", "")
        event.location = item.get("location", "")

        # Add a 15-minute reminder before each event
        event.alarms = [
            {
                "action": "display",
                "trigger": {"minutes": -15}
            }
        ]

        cal.events.add(event)

    # Generate unique filename
    uid = str(uuid.uuid4())
    filename = f"{uid}.ics"
    filepath = os.path.join(ics_dir, filename)

    # Save .ics file
    with open(filepath, "w") as f:
        f.writelines(cal)

    download_url = request.url_root.rstrip("/") + f"/ics/{filename}"
    return jsonify({"downloadUrl": download_url})

@app.route("/ics/<filename>")
def download_ics_file(filename):
    return send_from_directory(ics_dir, filename, as_attachment=True, mimetype='text/calendar')

@app.route("/openapi.yaml")
def serve_openapi_spec():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

@app.route("/")
def index():
    return "ICS API is running. Use /generate to create events."
