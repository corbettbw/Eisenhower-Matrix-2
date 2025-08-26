from flask import Flask, render_template, request, redirect, url_for
from itertools import count
from services import schedule_tasks
from flask import jsonify

app = Flask(__name__)

@app.post("/assignments/<int:aid>/delete")
def delete_assignment(aid):
    # remove the assignment (and all its tasks with it)
    global ASSIGNMENTS
    ASSIGNMENTS = [a for a in ASSIGNMENTS if a.get("id") != aid]
    return redirect(url_for("index"))

@app.get("/api/state")
def get_state():
    return jsonify({"assignments": ASSIGNMENTS, "tasks": TASKS})

@app.post("/api/state")
def set_state():
    data = request.get_json(force=True) or {}
    # Replace in-memory state
    global ASSIGNMENTS, TASKS
    ASSIGNMENTS = data.get("assignments", []) or []
    TASKS       = data.get("tasks", []) or []
    # Normalize IDs & reseed counters so future adds don’t collide
    _normalize_ids()
    return jsonify({"ok": True})



ASSIGNMENTS = []  # [{id, title, due_date, tasks: [ ... ]}]
TASKS = []
_next_aid = count(1)
_next_tid = count(1)

from itertools import count

# existing
# _next_aid = count(1)
# _next_tid = count(1)

def _normalize_ids():
    """Ensure all assignment/task IDs are unique ints and reseed counters."""
    global _next_aid, _next_tid, ASSIGNMENTS, TASKS

    # coerce to ints and find current maxes
    max_a = 0
    max_t = 0
    for a in ASSIGNMENTS:
        try: a["id"] = int(a.get("id"))
        except: a["id"] = None
        max_a = max(max_a, a["id"] or 0)
        a.setdefault("importance", 5)
        a.setdefault("tasks", [])
        for t in a["tasks"]:
            try: t["id"] = int(t.get("id"))
            except: t["id"] = None
            max_t = max(max_t, t["id"] or 0)
            t.setdefault("order", 1)

    for t in TASKS:
        try: t["id"] = int(t.get("id"))
        except: t["id"] = None
        max_t = max(max_t, t["id"] or 0)
        t.setdefault("importance", 5)
        t.setdefault("order", 1)

    # seed counters to avoid collisions
    _next_aid = count(max_a + 1)
    _next_tid = count(max_t + 1)

    # dedupe: assign fresh IDs where missing or duplicated
    seen_a = set()
    for a in ASSIGNMENTS:
        if not a["id"] or a["id"] in seen_a:
            a["id"] = next(_next_aid)
        seen_a.add(a["id"])

    seen_t = set()
    for t in TASKS:
        if not t["id"] or t["id"] in seen_t:
            t["id"] = next(_next_tid)
        seen_t.add(t["id"])

    for a in ASSIGNMENTS:
        for t in a["tasks"]:
            if not t["id"] or t["id"] in seen_t:
                t["id"] = next(_next_tid)
            seen_t.add(t["id"])


def _ensure_ids_and_defaults():
    """Give IDs to any assignments/tasks that don't have them (e.g., from ICS import)."""
    global ASSIGNMENTS, TASKS
    for a in ASSIGNMENTS:
        if "id" not in a:
            a["id"] = next(_next_aid)
        a.setdefault("importance", 5)
        a.setdefault("tasks", [])
        for t in a["tasks"]:
            if "id" not in t:
                t["id"] = next(_next_tid)
            t.setdefault("order", 1)
            # importance for assignment tasks is inherited during schedule; ok if absent

    for t in TASKS:
        if "id" not in t:
            t["id"] = next(_next_tid)
        t.setdefault("importance", 5)
        t.setdefault("order", 1)

def get_assignment(aid: int):
    return next((a for a in ASSIGNMENTS if a["id"] == aid), None)

def find_task(task_id: int):               # ⬅️ NEW: search standalone first, then assignments
    for t in TASKS:
        if t["id"] == task_id:
            return None, t
    for a in ASSIGNMENTS:
        for t in a["tasks"]:
            if t["id"] == task_id:
                return a, t
    return None, None

def schedule_assignment(a):
    if not a["tasks"]:
        return
    # order inside the assignment

    for t in a["tasks"]:
        t["importance"] = a["importance"]

    ordered = sorted(a["tasks"], key=lambda t: int(t.get("order", 0)))

    # feed a compact list into schedule_tasks() (finish-by = assignment due)
    tmp = [
        {
            "tid": t["id"],
            "title": t.get("title", ""),
            "due_date": a["due_date"],
            "duration_days": float(t.get("duration_days", 1)),
            "importance": int(t.get("importance", 0)),
        }
        for t in ordered
    ]
    schedule_tasks(tmp)  # adds start_date (str) and sorts by start

    start_by_tid = {row["tid"]: row["start_date"] for row in tmp}
    for t in a["tasks"]:
        t["start_date"] = start_by_tid[t["id"]]

    # keep display order stable: start asc, then priority desc, then order
    a["tasks"] = sorted(
        a["tasks"],
        key=lambda t: (t["start_date"], int(t.get("order", 0)))
    )

def schedule_all():                        # schedule standalone + each assignment
    if TASKS:
        schedule_tasks(TASKS)              # standalone tasks scheduled independently
    for a in ASSIGNMENTS:
        schedule_assignment(a)

def tasks_by_start():
    flat = []
    for t in TASKS:
        flat.append({
            "id": t["id"],
            "title": t["title"],
            "description": t.get("description", ""),
            "duration_days": t.get("duration_days", 1),
            "importance": t.get("importance", 0),
            "order": t.get("order", 0),
            "completed": t.get("completed", False),
            "start_date": t.get("start_date", ""),
            "due_date": t.get("due_date", ""),
            "assignment_id": None,
            "assignment_title": None,
        })

    for a in ASSIGNMENTS:
        for t in a.get("tasks", []):
            flat.append({
                "id": t["id"],
                "title": t["title"],
                "description": t.get("description", ""),
                "duration_days": t.get("duration_days", 1),
                "importance": a.get("importance", 0),
                "order": t.get("order", 0),
                "completed": t.get("completed", False),
                "start_date": t.get("start_date", ""),
                "due_date": a["due_date"],
                "assignment_id": a["id"],
                "assignment_title": a["title"],
            })

    flat.sort(key=lambda t: (t["start_date"], -int(t.get("importance", 0)), t["assignment_id"] or 0, int(t.get("order", 0))))
    return flat

@app.get("/")
def index():
    schedule_all()
    return render_template(
        "index.html",
        assignments=ASSIGNMENTS,
        tasks=tasks_by_start(),
    )

@app.post("/assignments")
def create_assignment():
    ASSIGNMENTS.append({
        "id": next(_next_aid),
        "title": request.form["assignment_title"].strip(),
        "due_date": request.form["assignment_due"],  # "YYYY-MM-DD"
        "importance": int(request.form.get("assignment_importance", 5)),
        "tasks": [],
    })
    return redirect(url_for("index"))

@app.post("/tasks")
def create_task():
    aid_raw = request.form.get("assignment_id")
    aid = int(aid_raw) if (aid_raw and aid_raw.isdigit()) else 0

    base = {
        "id": next(_next_tid),
        "title": request.form["title"].strip(),
        "description": request.form.get("description", "").strip(),
        "duration_days": float(request.form.get("duration_days", 1)),
        "order": int(request.form.get("order", 1)),
        "completed": False,
    }

    if aid > 0:
        a = get_assignment(aid)
        if a:
            base["importance"] = a["importance"]
            a["tasks"].append(base)
            return redirect(url_for("index"))
        # fall through if assignment not found -> standalone

    base["due_date"] = request.form.get("due_date") or ""
    base["importance"] = int(request.form.get("importance", 5))
    TASKS.append(base)
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/edit")
def edit_task(task_id):
    a, t = find_task(task_id)
    if not t:
        return redirect(url_for("index"))
    
    t["title"] = request.form["title"].strip()
    t["description"] = request.form.get("description", "").strip()
    t["duration_days"] = float(request.form.get("duration_days", 1))
    t["order"] = int(request.form.get("order", 1))

    if a is None:
        t["due_date"] = request.form["due_date"]
        t["importance"] = int(request.form.get("importance", 5))

    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/complete")
def complete_task(task_id):
    a, t = find_task(task_id)
    if t:
        t["completed"] = True
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/uncomplete")
def uncomplete_task(task_id):
    a, t = find_task(task_id)
    if t:
        t["completed"] = False
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    global TASKS
    TASKS = [t for t in TASKS if t["id"] != task_id]
    for a in ASSIGNMENTS:
        a["tasks"] = [t for t in a["tasks"] if t["id"] != task_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
