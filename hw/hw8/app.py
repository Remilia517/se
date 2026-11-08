from __future__ import annotations

import csv
import io
import os
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, url_for

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("STUDENT_HUB_DB", BASE / "student_hub.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "studyflow-2-demo-key-change-me")


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            course TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT '普通',
            status TEXT NOT NULL DEFAULT '待處理',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        """)
        if db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
            samples = [
                ("資料庫正規化報告", "資料庫系統", "整理 1NF、2NF、3NF 並製作 PDF。", "2026-11-10", "高", "進行中"),
                ("HTTP Client 程式測試", "軟體工程", "完成 MiniCurl 的 GET、POST 與錯誤處理測試。", "2026-11-12", "中", "待處理"),
                ("人工智慧實務作業", "人工智慧實務", "整理模型實驗結果與課堂心得。", "2026-11-15", "高", "待處理"),
                ("計算機網路習題", "計算機網路", "完成封包欄位與 TCP/IP 題目。", "2026-11-08", "低", "已完成"),
            ]
            db.executemany(
                """INSERT INTO tasks
                (title, course, description, due_date, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [(*row, datetime.now().isoformat(timespec="seconds")) for row in samples],
            )


def get_tasks(search=""):
    with connect() as db:
        if search:
            pattern = f"%{search}%"
            rows = db.execute("""
                SELECT * FROM tasks
                WHERE title LIKE ? OR course LIKE ? OR description LIKE ?
                ORDER BY CASE status WHEN '已完成' THEN 1 ELSE 0 END, due_date ASC, id DESC
            """, (pattern, pattern, pattern)).fetchall()
        else:
            rows = db.execute("""
                SELECT * FROM tasks
                ORDER BY CASE status WHEN '已完成' THEN 1 ELSE 0 END, due_date ASC, id DESC
            """).fetchall()
    return rows


@app.template_filter("date_label")
def date_label(value):
    try:
        return date.fromisoformat(value).strftime("%Y/%m/%d")
    except (TypeError, ValueError):
        return value


@app.route("/")
def dashboard():
    tasks = get_tasks()
    today = date.today()
    active = [t for t in tasks if t["status"] != "已完成"]
    overdue = [t for t in active if t["due_date"] < today.isoformat()]
    upcoming = [t for t in active if t["due_date"] >= today.isoformat()]
    completed = [t for t in tasks if t["status"] == "已完成"]
    completion = round(len(completed) / len(tasks) * 100) if tasks else 0

    course_stats = defaultdict(lambda: {"total": 0, "completed": 0})
    for task in tasks:
        course = task["course"] or "未分類"
        course_stats[course]["total"] += 1
        if task["status"] == "已完成":
            course_stats[course]["completed"] += 1
    courses = [
        {"name": name, "total": value["total"], "completed": value["completed"],
         "rate": round(value["completed"] / value["total"] * 100)}
        for name, value in sorted(course_stats.items())
    ]
    week_end = today + timedelta(days=7)
    week_tasks = [t for t in active if today.isoformat() <= t["due_date"] <= week_end.isoformat()]

    return render_template(
        "dashboard.html", tasks=tasks[:6], total=len(tasks), active=len(active),
        overdue=len(overdue), completed=len(completed), upcoming=len(upcoming),
        completion=completion, today=today.isoformat(), courses=courses,
        week_count=len(week_tasks)
    )


@app.route("/tasks")
def task_list():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    tasks = get_tasks(search)
    if status in {"待處理", "進行中", "已完成"}:
        tasks = [t for t in tasks if t["status"] == status]
    if priority in {"高", "中", "低"}:
        tasks = [t for t in tasks if t["priority"] == priority]
    return render_template("tasks.html", tasks=tasks, search=search, status=status, priority=priority)


@app.route("/calendar")
def calendar():
    month_text = request.args.get("month", date.today().strftime("%Y-%m"))
    try:
        month_start = date.fromisoformat(month_text + "-01")
    except ValueError:
        month_start = date.today().replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    tasks = get_tasks()
    grouped = defaultdict(list)
    for task in tasks:
        if task["due_date"].startswith(month_start.strftime("%Y-%m")):
            grouped[int(task["due_date"][-2:])].append(task)
    first_weekday, days_in_month = month_start.weekday(), (next_month - month_start).days
    cells = [None] * first_weekday + list(range(1, days_in_month + 1))
    while len(cells) % 7:
        cells.append(None)
    return render_template(
        "calendar.html", month=month_start.strftime("%Y-%m"),
        month_label=month_start.strftime("%Y 年 %m 月"),
        previous=previous_month.strftime("%Y-%m"), next=next_month.strftime("%Y-%m"),
        cells=cells, grouped=grouped, today=date.today().isoformat()
    )


@app.route("/export.csv")
def export_csv():
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(["編號", "事項名稱", "課程", "詳細說明", "截止日期", "優先級", "狀態", "建立時間"])
    for task in get_tasks():
        writer.writerow([task["id"], task["title"], task["course"], task["description"],
                         task["due_date"], task["priority"], task["status"], task["created_at"]])
    return Response(
        output.getvalue(), mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=studyflow_tasks.csv"}
    )


@app.route("/tasks/new", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        course = request.form.get("course", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", "中")
        if not title or not due_date:
            flash("事項名稱與截止日期為必填欄位。", "danger")
            return render_template("task_form.html", task=request.form, mode="新增")
        try:
            date.fromisoformat(due_date)
        except ValueError:
            flash("日期格式不正確。", "danger")
            return render_template("task_form.html", task=request.form, mode="新增")
        if priority not in {"高", "中", "低"}:
            priority = "中"
        with connect() as db:
            db.execute("""
                INSERT INTO tasks (title, course, description, due_date, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, '待處理', ?)
            """, (title, course, description, due_date, priority, datetime.now().isoformat(timespec="seconds")))
        flash("已新增作業／待辦事項。", "success")
        return redirect(url_for("task_list"))
    return render_template("task_form.html", task={}, mode="新增")


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    with connect() as db:
        task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task:
            flash("找不到指定事項。", "danger")
            return redirect(url_for("task_list"))
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            due_date = request.form.get("due_date", "").strip()
            if not title or not due_date:
                flash("事項名稱與截止日期為必填欄位。", "danger")
                return render_template("task_form.html", task=request.form, mode="編輯")
            try:
                date.fromisoformat(due_date)
            except ValueError:
                flash("日期格式不正確。", "danger")
                return render_template("task_form.html", task=request.form, mode="編輯")
            priority = request.form.get("priority", "中")
            if priority not in {"高", "中", "低"}:
                priority = "中"
            status = request.form.get("status", "待處理")
            if status not in {"待處理", "進行中", "已完成"}:
                status = "待處理"
            db.execute("""
                UPDATE tasks SET title=?, course=?, description=?, due_date=?, priority=?, status=? WHERE id=?
            """, (title, request.form.get("course", "").strip(),
                  request.form.get("description", "").strip(), due_date, priority, status, task_id))
            flash("事項已更新。", "success")
            return redirect(url_for("task_list"))
    return render_template("task_form.html", task=dict(task), mode="編輯")


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with connect() as db:
        task = db.execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()
        if task:
            new_status = "已完成" if task["status"] != "已完成" else "待處理"
            db.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
            flash("事項狀態已更新。", "success")
    return redirect(request.referrer or url_for("task_list"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    with connect() as db:
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    flash("事項已刪除。", "info")
    return redirect(request.referrer or url_for("task_list"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="找不到指定頁面。"), 404


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
