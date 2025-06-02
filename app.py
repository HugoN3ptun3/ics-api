from flask import Flask, request, jsonify, send_from_directory
from ics import Calendar, Event
import os
import uuid

app = Flask(__name__)
ics_dir = "ics_files"
os.makedirs(ics_dir, exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate_ics():
    data = request.json
    event = Event()
    event.name = data.get("title", "Untitled Event")
    event.begin = data["startTime"]
    event.end = data["endTime"]
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

@app.route("/ics/<filename>")
def serve_ics(filename):
    return send_from_directory(ics_dir, filename)

@app.route("/openapi.yaml")
def serve_openapi_spec():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

if __name__ == "__main__":
    app.run(debug=True)
