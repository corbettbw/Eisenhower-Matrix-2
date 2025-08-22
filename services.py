from datetime import datetime, timedelta

def schedule_tasks(tasks):
    # parse
    for t in tasks:
        t["_due"] = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
        t["_dur"] = float(t.get("duration_days", 1))
    # schedule backward: latest due first
    tasks.sort(key=lambda t: (t["_due"], -(int(t.get("importance") or 0))))
    earliest_finish = None
    for t in reversed(tasks):
        finish = t["_due"] if earliest_finish is None else min(t["_due"], earliest_finish)
        start = finish - timedelta(days=t["_dur"])
        t["_start"] = start
        earliest_finish = start
    # sort by start ascending and format for output
    tasks.sort(key=lambda t: t["_start"])
    
    for t in tasks:
        t["start_date"] = t["_start"].strftime("%Y-%m-%d")
        t["due_date"]   = t["_due"].strftime("%Y-%m-%d")
        for k in ("_start","_due","_dur"):
            t.pop(k, None)
    return tasks



# # Deliberately shuffled; includes overlaps, same-day due, and cascades
# tasks = [
#     {"title": "D: long task later (3d)", "due_date": "2025-09-08", "duration_days": 3},
#     {"title": "B: later due (2d)",       "due_date": "2025-09-05", "duration_days": 2},
#     {"title": "G: far future (2d)",      "due_date": "2025-09-20", "duration_days": 2},
#     {"title": "E: short early (1d)",     "due_date": "2025-09-02", "duration_days": 1},
#     {"title": "C: same day as B (1d)",   "due_date": "2025-09-05", "duration_days": 1},
#     {"title": "A: earlier due (2d)",     "due_date": "2025-09-04", "duration_days": 2},
#     {"title": "F: mid window (2d)",      "due_date": "2025-09-07", "duration_days": 2},
#     {"title": "H: tight window (2d)",    "due_date": "2025-09-06", "duration_days": 2},
# ]

# # tasks in reverse order:
# # G: September 20, duration: 2, Ideal Start Date: September 18, Actual Start Date: September 18 
# # D: September 8,  duration: 3, Ideal Start Date: September 5,  Actual Start Date: September 5
# # F: September 7,  Duration: 2, Ideal Start Date: September 5,  Actual Start Date: September 3
# # H: September 6,  Duration: 2, Ideal Start Date: September 4,  Actual Start Date: September 1
# # C: September 5,  Duration: 1, Ideal Start Date: September 4,  Actual Start Date: August 31
# # B: September 5,  Duration: 2, Ideal Start Date: September 3,  Actual Start Date: August 29
# # A: September 4,  Duration: 2, Ideal Start Date: September 2,  Actual Start Date: August 27
# # E: September 2,  Duration: 1, Ideal Start Date: September 1,  Actual Start Date: August 26

# schedule_tasks(tasks)
# for task in tasks :
#     print(task)

