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
    tz_name = data.get("timezone", "UTC")  # Default to UTC
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return jsonify({"error": "Invalid timezone"}), 400

    try:
        # Parse and localize times
