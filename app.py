from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory task list
tasks = []

@app.route("/")
def index():
    scheduled_tasks = schedule_tasks(tasks)
    return render_template("index.html", tasks=scheduled_tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    due = request.form["due"]
    duration = float(request.form["duration"])

    tasks.append({
        "title": title,
        "due": due,
        "duration": duration
    })
    return redirect("/")

@app.route("/sample")
def sample():
    global tasks
    tasks = [
        {"title": "Read article", "due": "2025-07-13", "duration": 1},
        {"title": "Write post", "due": "2025-07-15", "duration": 0.5},
        {"title": "Research", "due": "2025-07-14", "duration": 2},
    ]
    return redirect("/")

def schedule_tasks(task_list):
    scheduled = []
    for task in task_list:
        due_date = datetime.strptime(task["due"], "%Y-%m-%d")
        duration_days = timedelta(days=task["duration"])
        start_date = due_date - duration_days
        scheduled.append({
            "title": task["title"],
            "due": task["due"],
            "duration": task["duration"],
            "start": start_date.strftime("%Y-%m-%d")
        })
    return scheduled

if __name__ == "__main__":
    app.run(debug=True)
