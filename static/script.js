function runDemo() {
  const sampleTasks = [
    { name: "Read article", due_date: "2025-07-13", duration_days: 1 },
    { name: "Write post", due_date: "2025-07-15", duration_days: 0.5 },
    { name: "Research", due_date: "2025-07-14", duration_days: 2 }
  ];

  fetch("/api/schedule", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tasks: sampleTasks })
  })
    .then(res => res.json())
    .then(renderTasks);
}

function renderTasks(tasks) {
  const container = document.getElementById("task-list");
  container.innerHTML = "";

  tasks.forEach(task => {
    const div = document.createElement("div");
    div.innerHTML = `
      <strong>${task.name}</strong><br>
      Due: ${task.due_date}<br>
      Duration: ${task.duration_days} day(s)<br>
      <span style="color: green;">Start by: ${task.start_date}</span>
      <hr>
    `;
    container.appendChild(div);
  });
}

function renderTasks(tasks) {
  const container = document.getElementById("task-list");
  container.innerHTML = ""; // Clear existing tasks

  tasks.forEach(task => {
    const taskDiv = document.createElement("div");
    taskDiv.className = "task";

    taskDiv.innerHTML = `
      <strong>${task.name}</strong><br>
      Due: ${task.due_date}<br>
      Duration: ${task.duration_days} day(s)<br>
      <span style="color: green;">Start by: ${task.start_date}</span>
      <hr>
    `;

    container.appendChild(taskDiv);
  });
}
