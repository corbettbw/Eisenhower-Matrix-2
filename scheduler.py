from datetime import datetime, timedelta

def schedule_tasks(tasks):
    for task in tasks:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d")
        duration = int(task.get("duration_days", 1))
        start = due - timedelta(days=duration)
        task["start_date"] = start.strftime("%Y-%m-%d")
    return tasks
