from flask import Flask, render_template, request, jsonify
from scheduler import schedule_tasks

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    tasks = request.json.get("tasks", [])
    return jsonify(schedule_tasks(tasks))
