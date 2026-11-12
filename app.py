"""Small Flask LMS used as a local target for the automation exercises."""

import sqlite3
from contextlib import closing
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for


def create_app(database_path=None):
    app = Flask(__name__, template_folder="templates")
    app.config.update(SECRET_KEY="local-demo-secret-change-me", DATABASE=database_path or str(Path(__file__).parent / "instance" / "lms.sqlite"))
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    def connect():
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        return connection

    with closing(connect()) as connection, connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL, instructor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS enrollments (user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, progress INTEGER NOT NULL DEFAULT 0, UNIQUE(user_id, course_id));
        """)
        connection.execute("INSERT OR IGNORE INTO users (id, name, email, password) VALUES (1, 'Taylor Student', 'student@example.com', 'StudentPass123!')")
        if connection.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            connection.executemany("INSERT INTO courses (title, description, category, instructor) VALUES (?, ?, ?, ?)", [
                ("Python for Beginners", "Learn Python step by step with practical examples.", "Programming", "Morgan Lee"),
                ("Web Design Essentials", "Create clear and accessible web pages.", "Design", "Avery Kim"),
                ("Data Skills with SQL", "Query and understand relational data.", "Data", "Riley Chen"),
            ])

    def db():
        if "db" not in g:
            g.db = connect()
        return g.db

    @app.teardown_appcontext
    def close_db(_error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    def course_json(row):
        return {key: row[key] for key in ("id", "title", "description", "category", "instructor")}

    @app.get("/")
    def home():
        return redirect(url_for("courses"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name, email, password = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower(), request.form.get("password", "")
            if not name or not email or not password:
                flash("Please fill in all fields.", "error")
            elif "@" not in email:
                flash("Enter a valid email address.", "error")
            else:
                try:
                    db().execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                    db().commit()
                    flash("Account created. Please log in.", "success")
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    flash("An account with that email already exists.", "error")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = db().execute("SELECT * FROM users WHERE email = ? AND password = ?", (request.form.get("email", "").strip().lower(), request.form.get("password", ""))).fetchone()
            if user:
                session["user_id"] = user["id"]
                return redirect(url_for("dashboard"))
            flash("Invalid email or password", "error")
        return render_template("login.html")

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("courses"))

    @app.get("/courses")
    def courses():
        search, category = request.args.get("search", "").strip(), request.args.get("category", "").strip()
        rows = db().execute("SELECT * FROM courses WHERE title LIKE ? AND category LIKE ? ORDER BY id", (f"%{search}%", category or "%")).fetchall()
        return render_template("courses.html", courses=rows, selected_category=category, search=search)

    @app.get("/courses/<int:course_id>")
    def course_detail(course_id):
        course = db().execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
        return render_template("course_detail.html", course=course) if course else ("Course not found", 404)

    @app.post("/courses/<int:course_id>/enroll")
    @login_required
    def enroll(course_id):
        try:
            db().execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (session["user_id"], course_id))
            db().commit()
            flash("You are enrolled!", "success")
        except sqlite3.IntegrityError:
            flash("You are already enrolled in this course.", "error")
        return redirect(url_for("dashboard"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        user = db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        enrolled = db().execute("SELECT courses.*, enrollments.progress FROM courses JOIN enrollments ON courses.id = enrollments.course_id WHERE enrollments.user_id = ?", (session["user_id"],)).fetchall()
        return render_template("dashboard.html", user=user, courses=enrolled)

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        user = db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        if request.method == "POST":
            name, email = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower()
            password = request.form.get("password", "") or user["password"]
            if not name or "@" not in email:
                flash("Name and a valid email are required.", "error")
            else:
                try:
                    db().execute("UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?", (name, email, password, user["id"]))
                    db().commit()
                    flash("Profile updated.", "success")
                    return redirect(url_for("profile"))
                except sqlite3.IntegrityError:
                    flash("That email is already in use.", "error")
        return render_template("profile.html", user=user)

    @app.get("/api/courses")
    def api_courses():
        return jsonify([course_json(row) for row in db().execute("SELECT * FROM courses ORDER BY id").fetchall()])

    @app.get("/api/courses/<int:course_id>")
    def api_get_course(course_id):
        row = db().execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
        return (jsonify(course_json(row)), 200) if row else (jsonify({"error": "Course not found"}), 404)

    def course_payload():
        payload = request.get_json(silent=True)
        required = ("title", "description", "category", "instructor")
        if not isinstance(payload, dict) or any(not isinstance(payload.get(key), str) or not payload[key].strip() for key in required):
            return None
        return {key: payload[key].strip() for key in required}

    @app.post("/api/courses")
    def api_create_course():
        payload = course_payload()
        if payload is None:
            return jsonify({"error": "title, description, category, and instructor are required"}), 400
        cursor = db().execute("INSERT INTO courses (title, description, category, instructor) VALUES (?, ?, ?, ?)", tuple(payload.values()))
        db().commit()
        return jsonify(course_json(db().execute("SELECT * FROM courses WHERE id = ?", (cursor.lastrowid,)).fetchone())), 201

    @app.put("/api/courses/<int:course_id>")
    def api_put_course(course_id):
        payload = course_payload()
        if payload is None:
            return jsonify({"error": "title, description, category, and instructor are required"}), 400
        cursor = db().execute("UPDATE courses SET title = ?, description = ?, category = ?, instructor = ? WHERE id = ?", (*payload.values(), course_id))
        db().commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Course not found"}), 404
        return jsonify(course_json(db().execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()))

    @app.patch("/api/courses/<int:course_id>")
    def api_patch_course(course_id):
        payload = request.get_json(silent=True)
        allowed = {"title", "description", "category", "instructor"}
        if not isinstance(payload, dict) or not payload or any(key not in allowed or not isinstance(value, str) or not value.strip() for key, value in payload.items()):
            return jsonify({"error": "Provide at least one valid course field"}), 400
        fields = ", ".join(f"{key} = ?" for key in payload)
        cursor = db().execute(f"UPDATE courses SET {fields} WHERE id = ?", (*[value.strip() for value in payload.values()], course_id))
        db().commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Course not found"}), 404
        return jsonify(course_json(db().execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()))

    @app.delete("/api/courses/<int:course_id>")
    def api_delete_course(course_id):
        cursor = db().execute("DELETE FROM courses WHERE id = ?", (course_id,))
        db().commit()
        return ("", 204) if cursor.rowcount else (jsonify({"error": "Course not found"}), 404)

    return app


if __name__ == "__main__":
    create_app().run(debug=False)
