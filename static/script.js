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

// ---------- Local "database": localStorage ----------

function listKey(name) { return `todo:list:${name}`; }

async function fetchState() {
  const r = await fetch('/api/state'); return r.json();
}
async function pushState(state) {
  await fetch('/api/state', {method:'POST', headers:{'Content-Type':'application/json'},
                             body: JSON.stringify(state)});
}

function listSavedNames() {
  const names = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (k && k.startsWith('todo:list:')) names.push(k.slice('todo:list:'.length));
  }
  names.sort(); return names;
}

async function saveListFlow() {
  const name = prompt('Save list as:');
  if (!name) return;
  const state = await fetchState();
  localStorage.setItem(listKey(name), JSON.stringify(state));
  populateSavedLists();
  alert(`Saved "${name}".`);
}

function populateSavedLists() {
  const sel = document.getElementById('saved-lists');
  if (!sel) return;
  const cur = sel.value;
  sel.innerHTML = '<option value="">Open saved list…</option>';
  for (const n of listSavedNames()) {
    const opt = document.createElement('option'); opt.value = n; opt.textContent = n;
    sel.appendChild(opt);
  }
  if ([...sel.options].some(o => o.value === cur)) sel.value = cur;
}

async function openListFlow() {
  const sel = document.getElementById('saved-lists');
  const name = sel && sel.value;
  if (!name) { alert('Pick a saved name.'); return; }
  const raw = localStorage.getItem(listKey(name));
  if (!raw) { alert('Missing data for that name.'); return; }
  const state = JSON.parse(raw);
  await pushState(state);
  location.reload();
}

// ---------- Share link (URL fragment, no server storage) ----------
// Small/medium lists only (URL can get long). For big lists, use "Export file".
async function shareLinkFlow() {
  const state = await fetchState();
  const json = JSON.stringify(state);
  const b64 = btoa(unescape(encodeURIComponent(json)));  // UTF-8 safe
  const url = `${location.origin}${location.pathname}#share=${b64}`;
  await navigator.clipboard?.writeText(url);
  alert('Shareable link copied to clipboard.\nNote: for very large lists, use Export instead.');
}

// On load: if there's a #share=... fragment, offer to open it
(async function autoOpenShared() {
  const m = location.hash.match(/^#share=([\s\S]+)/);
  if (!m) return;
  try {
    const json = decodeURIComponent(escape(atob(m[1])));
    const state = JSON.parse(json);
    if (confirm('Open shared list from link?')) {
      await pushState(state); location.hash = ''; location.reload();
    }
  } catch (e) {
    console.error('Bad share payload', e);
  }
})();

// ---------- Import/Export as encrypted file (optional simple, unencrypted shown) ----------
// Minimal: plain JSON file (unencrypted). For encryption, we can add WebCrypto later.
async function exportFileFlow() {
  const state = await fetchState();
  const blob = new Blob([JSON.stringify(state, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `todo-list-${new Date().toISOString().slice(0,19).replace(/[:T]/g,'-')}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function importFileFlow() {
  const input = document.getElementById('file-import-list');
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();
    const state = JSON.parse(text);
    await pushState(state);
    alert('Imported. Reloading…'); location.reload();
  };
  input.click();
}

// ---------- Calendar (.ics) export ----------
function pad(n){return n.toString().padStart(2,'0');}
function ymdToDate(s){ const [y,m,d]=s.split('-').map(Number); return new Date(y, m-1, d); }
function dateToICS(d){ return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}`; }
function addDays(d, n){ const x = new Date(d); x.setDate(x.getDate()+n); return x; }

async function exportICSFlow() {
  const state = await fetch('/api/state').then(r => r.json());
  // pick a filename: saved-list dropdown value or prompt fallback
  const savedSel = document.getElementById('saved-lists');
  let baseName = (savedSel && savedSel.value) ? savedSel.value : (prompt('File name (no extension):','my-list') || 'todo-list');

  const now = new Date();
  const dtstamp = now.toISOString().replace(/[-:]/g,'').split('.')[0] + 'Z';
  const lines = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//YourApp//ToDo//EN'];

  let uidSeq = 0;

  // helper to add an all-day VEVENT for a task sized by duration_days
  function addTaskEvent(summary, desc, startYMD, durationDays) {
    if (!startYMD) return;
    const start = ymdToDate(startYMD);
    const end   = addDays(start, Math.max(1, Number(durationDays)||1)); // ICS DTEND is exclusive
    const uid = `todo-${++uidSeq}-${now.getTime()}@yourapp`;
    lines.push(
      'BEGIN:VEVENT',
      `UID:${uid}`,
      `DTSTAMP:${dtstamp}`,
      `DTSTART;VALUE=DATE:${dateToICS(start)}`,
      `DTEND;VALUE=DATE:${dateToICS(end)}`,
      `SUMMARY:${(summary||'').replace(/\r?\n/g,' ')}`,
      `DESCRIPTION:${(desc||'').replace(/\r?\n/g,' ')}`,
      'END:VEVENT'
    );
  }

  // standalone tasks: size by their own duration_days
  for (const t of state.tasks || []) {
    addTaskEvent(t.title, t.description, t.start_date, t.duration_days);
    // OPTIONAL milestone on due date (comment out if not wanted):
    // if (t.due_date) addTaskEvent(`Due: ${t.title}`, t.description, t.due_date, 1);
  }

  // assignment tasks: size by task.duration_days (NOT start→assignment due)
  for (const a of state.assignments || []) {
    for (const t of a.tasks || []) {
      addTaskEvent(`${a.title}: ${t.title}`, t.description, t.start_date, t.duration_days);
      // OPTIONAL milestone for assignment due:
      // addTaskEvent(`Due: ${a.title}`, '', a.due_date, 1);
    }
  }

  lines.push('END:VCALENDAR');

  const blob = new Blob([lines.join('\r\n')], {type:'text/calendar'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${baseName}.ics`;   // <- list-based filename
  a.click();
  URL.revokeObjectURL(a.href);
}


// ---------- Wire buttons ----------
document.addEventListener('DOMContentLoaded', () => {
  populateSavedLists();

  const byId = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };
  byId('btn-save-list',   saveListFlow);
  byId('btn-open-list',   openListFlow);
  byId('btn-share-link',  shareLinkFlow);
  byId('btn-export-ics',  exportICSFlow);
  byId('btn-import-file', importFileFlow);
});
