from __future__ import annotations

import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("KNU_PORTAL_DB", BASE_DIR / "knu_portal.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            grade INTEGER NOT NULL,
            email TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            teacher TEXT NOT NULL,
            credits INTEGER NOT NULL,
            day INTEGER NOT NULL,
            period_start INTEGER NOT NULL,
            period_end INTEGER NOT NULL,
            classroom TEXT NOT NULL,
            capacity INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            posted_at TEXT NOT NULL
        );
        """)

        student_count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if student_count == 0:
            db.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                ("412630001", "123456", "王小明", "資訊工程學系", 3, "s412630001@nkust.edu.tw")
            )
        course_count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        if course_count == 0:
            courses = [
                ("CS301", "資料庫系統", "陳老師", 3, 1, 2, 4, "E402", 60),
                ("CS302", "軟體工程", "林老師", 3, 2, 5, 7, "E305", 55),
                ("CS303", "計算機網路", "張老師", 3, 3, 2, 4, "E401", 50),
                ("CS304", "人工智慧實務", "黃老師", 3, 4, 6, 8, "E501", 45),
                ("GE201", "體育－羽球", "吳老師", 1, 5, 2, 3, "體育館", 35),
                ("CS305", "資料結構", "周老師", 3, 1, 6, 8, "E403", 60),
                ("CS306", "網頁程式設計", "許老師", 2, 3, 6, 7, "E302", 40),
                ("GE202", "英文溝通", "李老師", 2, 5, 5, 6, "B201", 45),
            ]
            db.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", courses)
            db.executemany(
                "INSERT INTO enrollments VALUES (?, ?)",
                [("412630001", "CS301"), ("412630001", "CS302"), ("412630001", "CS303")]
            )
        announcement_count = db.execute("SELECT COUNT(*) FROM announcements").fetchone()[0]
        if announcement_count == 0:
            db.executemany(
                "INSERT INTO announcements (title, content, posted_at) VALUES (?, ?, ?)",
                [
                    ("選課系統操作公告", "本系統為課堂專題展示，提供課程查詢、加選與退選的模擬功能。", "2026-11-01"),
                    ("期中成績查詢", "期中成績已開放查詢，請同學確認個人成績資料。", "2026-10-28"),
                    ("校園資訊系統維護", "系統維護期間請勿重複送出表單。", "2026-10-20"),
                ]
            )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "student_id" not in session:
            flash("請先登入學生帳號。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    if "student_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            student = db.execute(
                "SELECT * FROM students WHERE student_id = ? AND password = ?",
                (student_id, password)
            ).fetchone()
        if student:
            session.clear()
            session["student_id"] = student["student_id"]
            session["student_name"] = student["name"]
            flash(f"歡迎回來，{student['name']}！", "success")
            return redirect(url_for("dashboard"))
        flash("學號或密碼錯誤，請再試一次。", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("已安全登出。", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    sid = session["student_id"]
    with get_db() as db:
        student = db.execute("SELECT * FROM students WHERE student_id = ?", (sid,)).fetchone()
        courses = db.execute("""
            SELECT c.* FROM courses c
            JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.student_id = ?
            ORDER BY c.day, c.period_start
        """, (sid,)).fetchall()
        announcements = db.execute(
            "SELECT * FROM announcements ORDER BY posted_at DESC, id DESC LIMIT 5"
        ).fetchall()
    credits = sum(c["credits"] for c in courses)
    return render_template("dashboard.html", student=student, courses=courses,
                           announcements=announcements, credits=credits)


@app.route("/courses")
@login_required
def courses():
    keyword = request.args.get("q", "").strip()
    sid = session["student_id"]
    with get_db() as db:
        rows = db.execute("""
            SELECT c.*,
              (SELECT COUNT(*) FROM enrollments e WHERE e.course_id = c.course_id) AS enrolled,
              EXISTS(SELECT 1 FROM enrollments e
                     WHERE e.course_id = c.course_id AND e.student_id = ?) AS selected
            FROM courses c
            WHERE c.course_id LIKE ? OR c.name LIKE ? OR c.teacher LIKE ?
            ORDER BY c.course_id
        """, (sid, f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
    return render_template("courses.html", courses=rows, keyword=keyword)


def periods_overlap(a_start, a_end, b_start, b_end):
    return a_start <= b_end and b_start <= a_end


@app.post("/courses/<course_id>/add")
@login_required
def add_course(course_id):
    sid = session["student_id"]
    with get_db() as db:
        course = db.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,)).fetchone()
        if not course:
            flash("找不到這門課程。", "danger")
            return redirect(url_for("courses"))
        current = db.execute("""
            SELECT c.* FROM courses c JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.student_id = ?
        """, (sid,)).fetchall()
        if any(c["course_id"] == course_id for c in current):
            flash("你已經選過這門課程。", "warning")
        elif any(c["day"] == course["day"] and periods_overlap(
            c["period_start"], c["period_end"], course["period_start"], course["period_end"]
        ) for c in current):
            flash("加選失敗：課程時間與已選課程衝堂。", "danger")
        else:
            count = db.execute(
                "SELECT COUNT(*) FROM enrollments WHERE course_id = ?", (course_id,)
            ).fetchone()[0]
            if count >= course["capacity"]:
                flash("加選失敗：課程已額滿。", "danger")
            else:
                db.execute("INSERT INTO enrollments VALUES (?, ?)", (sid, course_id))
                flash(f"成功加選：{course['name']}。", "success")
    return redirect(url_for("courses"))


@app.post("/courses/<course_id>/drop")
@login_required
def drop_course(course_id):
    sid = session["student_id"]
    with get_db() as db:
        row = db.execute("""
            SELECT c.name FROM courses c JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.student_id = ? AND e.course_id = ?
        """, (sid, course_id)).fetchone()
        if row:
            db.execute("DELETE FROM enrollments WHERE student_id = ? AND course_id = ?",
                       (sid, course_id))
            flash(f"已退選：{row['name']}。", "success")
        else:
            flash("你尚未選修這門課程。", "warning")
    return redirect(url_for("courses"))


@app.route("/timetable")
@login_required
def timetable():
    sid = session["student_id"]
    with get_db() as db:
        courses = db.execute("""
            SELECT c.* FROM courses c JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.student_id = ? ORDER BY c.day, c.period_start
        """, (sid,)).fetchall()
    return render_template("timetable.html", courses=courses)


@app.route("/grades")
@login_required
def grades():
    # Demonstration records; clearly labelled as sample data.
    records = [
        ("CS301", "資料庫系統", 86, 88, 87),
        ("CS302", "軟體工程", 91, 90, 91),
        ("CS303", "計算機網路", 78, 84, 81),
    ]
    return render_template("grades.html", records=records)


@app.route("/profile")
@login_required
def profile():
    with get_db() as db:
        student = db.execute("SELECT * FROM students WHERE student_id = ?",
                             (session["student_id"],)).fetchone()
    return render_template("profile.html", student=student)


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="找不到你要瀏覽的頁面。"), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("error.html", code=500, message="系統發生錯誤，請稍後再試。"), 500


init_db()

if __name__ == "__main__":
    app.run(debug=True)
