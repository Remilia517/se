from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("STUDENT_HUB_DB", BASE / "student_hub.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "student-hub-demo-key-change-me")


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
                ORDER BY CASE status WHEN '已完成' THEN 1 ELSE 0 END,
                         due_date ASC, id DESC
            """, (pattern, pattern, pattern)).fetchall()
        else:
            rows = db.execute("""
                SELECT * FROM tasks
                ORDER BY CASE status WHEN '已完成' THEN 1 ELSE 0 END,
                         due_date ASC, id DESC
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
    today = date.today().isoformat()
    active = [t for t in tasks if t["status"] != "已完成"]
    overdue = [t for t in active if t["due_date"] < today]
    upcoming = [t for t in active if t["due_date"] >= today]
    completed = [t for t in tasks if t["status"] == "已完成"]
    completion = round(len(completed) / len(tasks) * 100) if tasks else 0
    return render_template(
        "dashboard.html", tasks=tasks[:6], total=len(tasks), active=len(active),
        overdue=len(overdue), completed=len(completed), upcoming=len(upcoming),
        completion=completion, today=today
    )


@app.route("/tasks")
def task_list():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    tasks = get_tasks(search)
    if status in {"待處理", "進行中", "已完成"}:
        tasks = [t for t in tasks if t["status"] == status]
    return render_template("tasks.html", tasks=tasks, search=search, status=status)


@app.route("/tasks/new", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        course = request.form.get("course", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "").strip()
        priority = request.form.get("priority", "普通")
        if not title or not due_date:
            flash("作業名稱與截止日期為必填欄位。", "danger")
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
            """, (title, course, description, due_date, priority,
                  datetime.now().isoformat(timespec="seconds")))
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
                flash("作業名稱與截止日期為必填欄位。", "danger")
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
                UPDATE tasks SET title=?, course=?, description=?, due_date=?,
                    priority=?, status=? WHERE id=?
            """, (title, request.form.get("course", "").strip(),
                  request.form.get("description", "").strip(), due_date,
                  priority, status, task_id))
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
    return redirect(url_for("task_list"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="找不到指定頁面。"), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
