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
        start = tz.localize(datetime.fromisoformat(data["startTime"]))
        end = tz.localize(datetime.fromisoformat(data["endTime"]))
    except Exception as e:
        return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400
