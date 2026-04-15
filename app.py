#!/usr/bin/env python3
"""
app.py — Flask web-based To-Do application.
Run: python app.py  →  open http://localhost:5000
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_data.json")

# ── Data layer ────────────────────────────────────────────────────────────────
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

# ── HTML Template ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>To-Do</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg:       #0f0f11;
    --surface:  #1a1a1f;
    --card:     #222228;
    --border:   #2e2e38;
    --accent:   #c8f055;
    --accent2:  #55f0c8;
    --muted:    #5a5a6e;
    --text:     #e8e8f0;
    --done-col: #3a3a45;
    --high:     #ff6b6b;
    --med:      #ffc947;
    --low:      #55f0c8;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    min-height: 100vh;
    padding: 2rem 1rem 4rem;
  }

  /* ── layout ── */
  .wrap { max-width: 740px; margin: 0 auto; }

  header {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 2.5rem;
  }
  header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    letter-spacing: -0.5px;
    color: var(--accent);
    line-height: 1;
  }
  .count-badge {
    background: var(--border);
    color: var(--muted);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: .78rem;
    font-weight: 500;
    letter-spacing: .04em;
  }

  /* ── add form ── */
  .add-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 2rem;
  }
  .add-card h2 {
    font-size: .75rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
  }
  .row { display: flex; gap: .75rem; flex-wrap: wrap; }
  .row.top { margin-bottom: .75rem; }
  input[type="text"], input[type="date"], select {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: .92rem;
    padding: .6rem 1rem;
    outline: none;
    transition: border-color .2s;
  }
  input[type="text"]:focus, input[type="date"]:focus, select:focus {
    border-color: var(--accent);
  }
  input[type="text"] { flex: 1 1 260px; }
  select { min-width: 130px; cursor: pointer; }
  input[type="date"] { min-width: 160px; }
  .btn {
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    font-size: .9rem;
    font-weight: 500;
    padding: .6rem 1.3rem;
    transition: opacity .15s, transform .1s;
  }
  .btn:active { transform: scale(.97); }
  .btn-add  { background: var(--accent); color: #111; }
  .btn-add:hover { opacity: .85; }

  /* ── filters ── */
  .filters {
    display: flex;
    gap: .5rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
  }
  .filter-btn {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    color: var(--muted);
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    font-size: .82rem;
    font-weight: 500;
    padding: .35rem .9rem;
    transition: background .15s, color .15s, border-color .15s;
    text-decoration: none;
  }
  .filter-btn.active, .filter-btn:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: #111;
  }

  /* ── task list ── */
  .task-list { display: flex; flex-direction: column; gap: .65rem; }

  .task-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color .2s, opacity .2s;
    position: relative;
  }
  .task-card.done-card { opacity: .5; }
  .task-card:hover { border-color: var(--muted); }

  /* checkbox */
  .check-wrap { flex-shrink: 0; }
  .check-wrap input[type="checkbox"] { display: none; }
  .check-wrap label {
    width: 22px; height: 22px;
    border: 2px solid var(--border);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: border-color .2s, background .2s;
    color: transparent;
    font-size: .8rem;
  }
  .check-wrap input:checked + label {
    background: var(--accent);
    border-color: var(--accent);
    color: #111;
  }
  .check-wrap label:hover { border-color: var(--accent); }

  .task-body { flex: 1; min-width: 0; }
  .task-title {
    font-size: 1rem;
    font-weight: 400;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .done-card .task-title { text-decoration: line-through; color: var(--muted); }
  .task-meta {
    display: flex; gap: .6rem; align-items: center; margin-top: .25rem; flex-wrap: wrap;
  }
  .tag {
    border-radius: 999px;
    font-size: .7rem;
    font-weight: 500;
    letter-spacing: .05em;
    padding: 2px 8px;
    text-transform: uppercase;
  }
  .p-high   { background: #ff6b6b22; color: var(--high); border: 1px solid #ff6b6b44; }
  .p-medium { background: #ffc94722; color: var(--med);  border: 1px solid #ffc94744; }
  .p-low    { background: #55f0c822; color: var(--low);  border: 1px solid #55f0c844; }
  .due-tag  { color: var(--muted); font-size: .75rem; }
  .overdue  { color: var(--high); }

  /* actions */
  .task-actions { display: flex; gap: .4rem; flex-shrink: 0; }
  .icon-btn {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--muted);
    cursor: pointer;
    font-size: .85rem;
    padding: .35rem .55rem;
    transition: background .15s, color .15s;
    text-decoration: none;
    display: inline-flex;
  }
  .icon-btn:hover { background: var(--border); color: var(--text); }
  .icon-btn.del:hover { background: #ff6b6b22; color: var(--high); border-color: #ff6b6b44; }

  /* edit modal */
  .modal-overlay {
    display: none;
    position: fixed; inset: 0;
    background: rgba(0,0,0,.7);
    z-index: 100;
    align-items: center; justify-content: center;
  }
  .modal-overlay.open { display: flex; }
  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.8rem;
    width: min(480px, 92vw);
  }
  .modal h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    margin-bottom: 1.2rem;
    color: var(--accent);
  }
  .field { margin-bottom: .9rem; }
  .field label { display: block; font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-bottom: .35rem; }
  .field input, .field select { width: 100%; }
  .modal-actions { display: flex; gap: .6rem; justify-content: flex-end; margin-top: 1.2rem; }
  .btn-cancel { background: var(--card); color: var(--muted); border: 1px solid var(--border); }
  .btn-save   { background: var(--accent); color: #111; }

  .empty { text-align: center; color: var(--muted); padding: 3rem 0; font-size: .95rem; }
  .empty span { display: block; font-size: 2.5rem; margin-bottom: .5rem; }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <h1>✦ To-Do</h1>
    <span class="count-badge">{{ pending }} pending</span>
  </header>

  <!-- Add form -->
  <div class="add-card">
    <h2>New Task</h2>
    <form method="POST" action="/add">
      <div class="row top">
        <input type="text" name="title" placeholder="What needs to be done?" required autocomplete="off"/>
        <select name="priority">
          <option value="low">Low priority</option>
          <option value="medium">Medium priority</option>
          <option value="high">High priority</option>
        </select>
      </div>
      <div class="row">
        <input type="date" name="due"/>
        <button class="btn btn-add" type="submit">+ Add Task</button>
      </div>
    </form>
  </div>

  <!-- Filters -->
  <div class="filters">
    <a class="filter-btn {% if filter=='all' %}active{% endif %}" href="/?filter=all">All ({{ total }})</a>
    <a class="filter-btn {% if filter=='pending' %}active{% endif %}" href="/?filter=pending">Pending ({{ pending }})</a>
    <a class="filter-btn {% if filter=='done' %}active{% endif %}" href="/?filter=done">Done ({{ done_count }})</a>
    <a class="filter-btn {% if filter=='high' %}active{% endif %}" href="/?filter=high">🔴 High</a>
    <a class="filter-btn {% if filter=='overdue' %}active{% endif %}" href="/?filter=overdue">⚠ Overdue</a>
  </div>

  <!-- Task list -->
  <div class="task-list">
    {% if tasks %}
      {% for t in tasks %}
      <div class="task-card {% if t.done %}done-card{% endif %}">

        <!-- Checkbox -->
        <div class="check-wrap">
          <form method="POST" action="/toggle/{{ t.id }}">
            <input type="checkbox" id="cb{{ t.id }}" {% if t.done %}checked{% endif %}
                   onchange="this.form.submit()"/>
            <label for="cb{{ t.id }}">✔</label>
          </form>
        </div>

        <!-- Body -->
        <div class="task-body">
          <div class="task-title">{{ t.title }}</div>
          <div class="task-meta">
            <span class="tag p-{{ t.priority }}">{{ t.priority }}</span>
            {% if t.due %}
              {% set overdue = not t.done and t.due < today %}
              <span class="due-tag {% if overdue %}overdue{% endif %}">
                {% if overdue %}⚠ {% endif %}{{ t.due }}
              </span>
            {% endif %}
          </div>
        </div>

        <!-- Actions -->
        <div class="task-actions">
          <button class="icon-btn" onclick="openEdit({{ t|tojson }})">✎</button>
          <form method="POST" action="/delete/{{ t.id }}"
                onsubmit="return confirm('Remove this task?')">
            <button class="icon-btn del" type="submit">✕</button>
          </form>
        </div>
      </div>
      {% endfor %}
    {% else %}
      <div class="empty"><span>🎉</span>Nothing here — add a task above!</div>
    {% endif %}
  </div>
</div>

<!-- Edit Modal -->
<div class="modal-overlay" id="editModal">
  <div class="modal">
    <h2>Edit Task</h2>
    <form method="POST" id="editForm" action="">
      <div class="field">
        <label>Title</label>
        <input type="text" name="title" id="editTitle" required/>
      </div>
      <div class="field">
        <label>Priority</label>
        <select name="priority" id="editPriority">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div class="field">
        <label>Due date</label>
        <input type="date" name="due" id="editDue"/>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-cancel" onclick="closeEdit()">Cancel</button>
        <button type="submit" class="btn btn-save">Save</button>
      </div>
    </form>
  </div>
</div>

<script>
function openEdit(task) {
  document.getElementById('editTitle').value    = task.title;
  document.getElementById('editPriority').value = task.priority;
  document.getElementById('editDue').value      = task.due || '';
  document.getElementById('editForm').action    = '/edit/' + task.id;
  document.getElementById('editModal').classList.add('open');
}
function closeEdit() {
  document.getElementById('editModal').classList.remove('open');
}
document.getElementById('editModal').addEventListener('click', function(e) {
  if (e.target === this) closeEdit();
});
</script>
</body>
</html>"""

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    tasks  = load_tasks()
    today  = datetime.now().strftime("%Y-%m-%d")
    f      = request.args.get("filter", "all")

    view = tasks
    if f == "pending":  view = [t for t in tasks if not t["done"]]
    elif f == "done":   view = [t for t in tasks if t["done"]]
    elif f == "high":   view = [t for t in tasks if t.get("priority") == "high"]
    elif f == "overdue":
        view = [t for t in tasks if t.get("due") and t["due"] < today and not t["done"]]

    return render_template_string(HTML,
        tasks      = view,
        total      = len(tasks),
        pending    = sum(1 for t in tasks if not t["done"]),
        done_count = sum(1 for t in tasks if t["done"]),
        filter     = f,
        today      = today,
    )

@app.route("/add", methods=["POST"])
def add():
    tasks = load_tasks()
    title = request.form.get("title", "").strip()
    if title:
        tasks.append({
            "id":       next_id(tasks),
            "title":    title,
            "done":     False,
            "priority": request.form.get("priority", "low"),
            "due":      request.form.get("due") or None,
            "created":  datetime.now().strftime("%Y-%m-%d"),
        })
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/toggle/<int:tid>", methods=["POST"])
def toggle(tid):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == tid:
            t["done"] = not t["done"]
            break
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))

@app.route("/delete/<int:tid>", methods=["POST"])
def delete(tid):
    tasks = [t for t in load_tasks() if t["id"] != tid]
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))

@app.route("/edit/<int:tid>", methods=["POST"])
def edit(tid):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == tid:
            t["title"]    = request.form.get("title", t["title"]).strip() or t["title"]
            t["priority"] = request.form.get("priority", t["priority"])
            t["due"]      = request.form.get("due") or None
            break
    save_tasks(tasks)
    return redirect(request.referrer or url_for("index"))

if __name__ == "__main__":
    print("  ✦  To-Do running →  http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
