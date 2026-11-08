import os, time
from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)
DB_URL = os.getenv("DATABASE_URL", "postgresql://studytask:studytask_password@db:5432/studytask")

def connect():
    return psycopg.connect(DB_URL, row_factory=dict_row)

def init_db():
    error = None
    for _ in range(20):
        try:
            with connect() as db:
                db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY, title VARCHAR(160) NOT NULL,
                    course VARCHAR(100) NOT NULL DEFAULT '', due_date DATE,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
            return
        except psycopg.OperationalError as exc:
            error = exc
            time.sleep(2)
    raise RuntimeError(f"PostgreSQL connection failed: {error}")

@app.get("/api/health")
def health():
    try:
        with connect() as db: db.execute("SELECT 1")
        return jsonify(status="ok", service="studytask-api", database="connected")
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 503

@app.get("/api/tasks")
def tasks():
    with connect() as db:
        rows = db.execute("""SELECT id,title,course,due_date,status FROM tasks ORDER BY id DESC""").fetchall()
    for row in rows:
        if row["due_date"]: row["due_date"] = row["due_date"].isoformat()
    return jsonify(rows)

@app.post("/api/tasks")
def add_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title: return jsonify(error="作業名稱不可空白"), 400
    try:
        with connect() as db:
            row = db.execute("""INSERT INTO tasks(title,course,due_date)
                VALUES(%s,%s,%s) RETURNING id,title,course,due_date,status""",
                (title, str(data.get("course", "")).strip(), data.get("due_date") or None)).fetchone()
        if row["due_date"]: row["due_date"] = row["due_date"].isoformat()
        return jsonify(row), 201
    except psycopg.errors.InvalidDatetimeFormat:
        return jsonify(error="日期格式錯誤，請使用 YYYY-MM-DD"), 400

@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in ("pending", "done"): return jsonify(error="status 必須是 pending 或 done"), 400
    with connect() as db:
        row = db.execute("""UPDATE tasks SET status=%s WHERE id=%s
            RETURNING id,title,course,due_date,status""", (status, task_id)).fetchone()
    if row is None: return jsonify(error="找不到這筆作業"), 404
    if row["due_date"]: row["due_date"] = row["due_date"].isoformat()
    return jsonify(row)

@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with connect() as db: result = db.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    if result.rowcount == 0: return jsonify(error="找不到這筆作業"), 404
    return jsonify(message="deleted")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
