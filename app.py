from flask import Flask, render_template, request, redirect, url_for
from itertools import count
from services import schedule_tasks

app = Flask(__name__)

TASKS = []
_next_id = count(1)

def get_task(task_id):
    for t in TASKS:
        if t["id"] == task_id:
            return t
    return None

@app.get("/")
def index():
    schedule_tasks(TASKS)  # recompute + sort
    return render_template("index.html", tasks=TASKS)

@app.post("/tasks")
def create_task():
    TASKS.append({
        "id": next(_next_id),
        "title": request.form["title"].strip(),
        "description": request.form.get("description", "").strip(),
        "due_date": request.form["due_date"],            # "YYYY-MM-DD"
        "duration_days": float(request.form.get("duration_days", 1)),
        "importance": int(request.form.get("importance", 5)),
        "completed": False,
    })
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/edit")
def edit_task(task_id):
    t = get_task(task_id)
    if t:
        t["title"] = request.form["title"].strip()
        t["description"] = request.form.get("description", "").strip()
        t["due_date"] = request.form["due_date"]
        t["duration_days"] = float(request.form.get("duration_days", 1))
        t["importance"] = int(request.form.get("importance", 5))
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/complete")
def complete_task(task_id):
    t = get_task(task_id)
    if t:
        t["completed"] = True
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/uncomplete")
def uncomplete_task(task_id):
    t = get_task(task_id)
    if t:
        t["completed"] = False
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    global TASKS
    TASKS = [t for t in TASKS if t["id"] != task_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
