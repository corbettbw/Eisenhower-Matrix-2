// Toggles Add Task form fields based on whether an assignment is selected.
(function () {
  function $(id) { return document.getElementById(id); }

  function refreshAddTask() {
    const select = $('assignment_id');
    if (!select) return;

    const isStandalone = (select.value === '0' || select.value === '');

    const standalone = $('standalone-fields'); // due_date + importance
    const assignOnly = $('assignment-fields'); // order

    const due  = $('due_date');
    const prio = $('importance');
    const order = $('order');

    // Show/hide groups (use `hidden` so layout is clean)
    if (standalone) standalone.hidden = !isStandalone;
    if (assignOnly) assignOnly.hidden = isStandalone;

    // Validation + submission behavior
    if (due)  { due.required = isStandalone; due.disabled = !isStandalone; if (!isStandalone) due.value = ''; }
    if (prio) { prio.disabled = !isStandalone; if (!isStandalone) prio.value = ''; }
    if (order){ order.disabled = isStandalone; if (isStandalone) order.value = '1'; }
  }

  document.addEventListener('DOMContentLoaded', refreshAddTask);
  document.addEventListener('change', (e) => {
    if (e.target && e.target.id === 'assignment_id') refreshAddTask();
  });

  // Optional: expose for manual calls if needed
  window.refreshAddTask = refreshAddTask;
})();
