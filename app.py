"""
Civisense – Smart Civic Issue Reporting & Tracking System
Backend Application (Flask + SQLite + AI Classifier)
"""

import os
import sqlite3
import random
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, abort, session
)


from model.classifier import analyze_issue

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "civisense-hackathon-secret-key-2026"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# Database Initialization & Helpers
# ---------------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create complaints table and seed initial hackathon demo records if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            name TEXT,
            contact TEXT,
            issue_type TEXT NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT,
            latitude REAL,
            longitude REAL,
            location TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            severity TEXT NOT NULL,
            priority INTEGER NOT NULL,
            department TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Reported',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT,
            phone TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Seed default users if empty
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        seed_users = [
            (
                "admin", "admin@civisense.gov", "admin123",
                "Municipal Commissioner (Admin)", "admin",
                "Nagpur Municipal Corporation (Central HQ)", "+91 712 2567890"
            ),
            (
                "citizen", "citizen@nagpur.in", "citizen123",
                "Rajesh Sharma", "citizen",
                None, "+91 98230 11234"
            ),
            (
                "sunita", "sunita.v@gmail.com", "citizen123",
                "Sunita Verma", "citizen",
                None, "+91 97654 44521"
            )
        ]
        cursor.executemany("""
            INSERT INTO users (username, email, password, name, role, department, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, seed_users)
        conn.commit()


    # Check if table already has data
    cursor.execute("SELECT COUNT(*) as count FROM complaints")
    count = cursor.fetchone()["count"]

    if count == 0:
        seed_complaints = [
            (
                "CIV-10482", "Rajesh Sharma", "+91 98230 11234", "Pothole",
                "Deep crater-like pothole in the middle of the road causing two-wheeler skidding and major evening traffic backlog.",
                "pothole_ward12.jpg", 21.1120, 79.0515, "Ward 12, Ring Road",
                94, "HIGH", 8, "Road Maintenance Department", "Reported",
                "2026-09-04 09:15:00"
            ),
            (
                "CIV-10483", "Sunita Verma", "+91 97654 44521", "Garbage Dump",
                "Severe roadside garbage pile dumped near the municipal playground. Stray dogs scattering waste and terrible odor.",
                "garbage_ward7.jpg", 21.1305, 79.0965, "Ward 7, Near Community Center",
                89, "MEDIUM", 6, "Solid Waste Management Department", "Assigned",
                "2026-09-03 14:30:00"
            ),
            (
                "CIV-10484", "Amitabh Kulkarni", "amitabh.k@gmail.com", "Broken Streetlight",
                "Entire line of streetlights non-operational for 4 consecutive nights. Road is pitch dark and hazardous for pedestrians.",
                "streetlight_ward4.jpg", 21.1520, 79.0620, "Ward 4, West End Avenue",
                96, "MEDIUM", 6, "Electrical & Public Lighting Department", "In Progress",
                "2026-09-02 18:45:00"
            ),
            (
                "CIV-10485", "Pooja Deshmukh", "+91 94221 88901", "Water Leakage",
                "Major underground drinking water supply pipe rupture. Clean potable water gushing on main road for 12 hours.",
                "water_leak_civillines.jpg", 21.1590, 79.0735, "Civil Lines, Near High Court Gate",
                93, "HIGH", 8, "Water Supply & Sewerage Board", "Resolved",
                "2026-08-31 08:20:00"
            ),
            (
                "CIV-10486", "Nitin Gadkari Jr.", "nitin.g@nagpurcitizen.org", "Road Damage",
                "Severe asphalt caving and structural crack along commercial market lane following heavy monsoon downpours.",
                "road_damage_sadar.jpg", 21.1630, 79.0830, "Sadar, Residency Road",
                91, "HIGH", 7, "Public Works Department (PWD)", "In Progress",
                "2026-09-01 11:10:00"
            ),
            (
                "CIV-10487", "Neha Tiwari", "+91 98812 33456", "Overflowing Drain",
                "Stormwater drain blocked with silt and domestic waste. Raw sewage overflowing into residential colony entrance.",
                "drain_manishnagar.jpg", 21.0960, 79.0810, "Manish Nagar, Besa Road Junction",
                95, "CRITICAL", 9, "Municipal Drainage & Sanitation Department", "Assigned",
                "2026-09-04 16:00:00"
            ),
            (
                "CIV-10488", "Dr. Anand Rao", "+91 94033 77112", "Pothole",
                "Dangerous deep pothole on blind turn near shopping arcade. Multiple close accidents witnessed.",
                "pothole_dharampeth.jpg", 21.1435, 79.0610, "Dharampeth Commercial Street",
                92, "HIGH", 8, "Road Maintenance Department", "Verified",
                "2026-09-04 12:40:00"
            ),
            (
                "CIV-10489", "Kavita Joshi", "+91 93710 99881", "Garbage Dump",
                "Illegal construction debris and broken masonry dumped on canal footpath preventing morning walkers.",
                "waste_ramdaspeth.jpg", 21.1340, 79.0760, "Ramdaspeth, Canal Walkway",
                88, "LOW", 4, "Solid Waste Management Department", "Reported",
                "2026-09-05 07:50:00"
            )
        ]
        cursor.executemany("""
            INSERT INTO complaints (
                complaint_id, name, contact, issue_type, description,
                image_path, latitude, longitude, location,
                confidence, severity, priority, department, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_complaints)
        conn.commit()

    conn.close()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_complaint_id():
    """Generates unique ID formatted like CIV-10482."""
    conn = get_db_connection()
    cursor = conn.cursor()
    while True:
        candidate = f"CIV-{random.randint(10000, 99999)}"
        cursor.execute("SELECT id FROM complaints WHERE complaint_id = ?", (candidate,))
        if not cursor.fetchone():
            conn.close()
            return candidate


def calculate_ai_insights(complaints):
    """Dynamically derives high-level actionable AI insights from complaints data."""
    insights = []
    if not complaints:
        return [
            {"icon": "info", "text": "No complaints registered yet. System ready for reporting."}
        ]

    total = len(complaints)
    high_priority = [c for c in complaints if c["priority"] >= 8 or c["severity"] in ("HIGH", "CRITICAL")]
    pending = [c for c in complaints if c["status"] != "Resolved"]
    potholes = [c for c in complaints if c["issue_type"] == "Pothole"]

    # Ward frequency
    ward_counts = {}
    for c in complaints:
        loc = c["location"]
        # Extract Ward if present
        if "Ward" in loc:
            parts = loc.split(",")
            ward = parts[0].strip()
            ward_counts[ward] = ward_counts.get(ward, 0) + 1
        elif "Civil Lines" in loc:
            ward_counts["Civil Lines"] = ward_counts.get("Civil Lines", 0) + 1
        elif "Sadar" in loc:
            ward_counts["Sadar"] = ward_counts.get("Sadar", 0) + 1
        elif "Manish Nagar" in loc:
            ward_counts["Manish Nagar"] = ward_counts.get("Manish Nagar", 0) + 1

    top_ward = max(ward_counts, key=ward_counts.get) if ward_counts else "Ward 12"

    pothole_pct = round((len(potholes) / total) * 100) if total else 0
    insights.append({
        "type": "trend",
        "badge": "SURGE DETECTED",
        "icon": "fa-arrow-trend-up",
        "color": "amber",
        "text": f"Pothole complaints represent {pothole_pct}% of civic logs this month."
    })

    insights.append({
        "type": "hotspot",
        "badge": "HOTSPOT ALERT",
        "icon": "fa-fire",
        "color": "red",
        "text": f"{top_ward} recorded the highest frequency of citizen complaints."
    })

    if high_priority:
        insights.append({
            "type": "urgent",
            "badge": "ACTION REQUIRED",
            "icon": "fa-triangle-exclamation",
            "color": "rose",
            "text": f"{len(high_priority)} high-priority complaints currently require immediate field team dispatch."
        })

    insights.append({
        "type": "recommendation",
        "badge": "SMART ROUTING",
        "icon": "fa-lightbulb",
        "color": "emerald",
        "text": f"Recommendation: Deploy rapid asphalt repair unit to {top_ward} corridor."
    })

    return insights


# ---------------------------------------------------------
# Application Web Routes
# ---------------------------------------------------------

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Aggregate statistics
    cursor.execute("SELECT COUNT(*) as total FROM complaints")
    total_issues = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status = 'Resolved'")
    resolved_issues = cursor.fetchone()["resolved"]

    cursor.execute("SELECT COUNT(*) as pending FROM complaints WHERE status != 'Resolved'")
    pending_issues = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) as high_priority FROM complaints WHERE priority >= 8 OR severity IN ('HIGH', 'CRITICAL')")
    high_priority_issues = cursor.fetchone()["high_priority"]

    # Recent complaints for spotlight
    cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC LIMIT 4")
    recent_complaints = cursor.fetchall()
    conn.close()

    return render_template(
        "index.html",
        total_issues=total_issues,
        resolved_issues=resolved_issues,
        pending_issues=pending_issues,
        high_priority_issues=high_priority_issues,
        recent_complaints=recent_complaints
    )


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        # Form inputs
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        name = request.form.get("name", "").strip()
        contact = request.form.get("contact", "").strip()
        lat_str = request.form.get("latitude", "").strip()
        lon_str = request.form.get("longitude", "").strip()

        # Validation
        if not description:
            flash("Please provide a brief description of the civic problem.", "error")
            return redirect(request.url)

        if not location:
            flash("Please enter the issue location or click 'Use Current Location'.", "error")
            return redirect(request.url)

        # Image handling
        image_file = request.files.get("image")
        selected_sample = request.form.get("selected_sample", "").strip()
        filename = None
        saved_file_path = None

        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                safe_name = secure_filename(image_file.filename)
                timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
                filename = f"{timestamp_prefix}{safe_name}"
                saved_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image_file.save(saved_file_path)
            else:
                flash("Invalid image format. Supported formats: JPG, PNG, WEBP, GIF.", "error")
                return redirect(request.url)
        elif selected_sample and os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], selected_sample)):
            # Citizen selected one of the real evidence presets
            import shutil
            safe_name = secure_filename(selected_sample)
            timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = f"{timestamp_prefix}{safe_name}"
            saved_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            shutil.copyfile(os.path.join(app.config["UPLOAD_FOLDER"], selected_sample), saved_file_path)
        else:
            # Fallback default real pothole image if citizen reports without uploading a photo
            filename = "pothole_ward12.jpg"
            saved_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)


        # Coordinate fallback to Nagpur center if not supplied
        try:
            latitude = float(lat_str) if lat_str else 21.1458
            longitude = float(lon_str) if lon_str else 79.0882
        except ValueError:
            latitude, longitude = 21.1458, 79.0882

        # Run AI Classifier
        ai_result = analyze_issue(image_path=saved_file_path, description=description)

        complaint_id = generate_complaint_id()
        citizen_name = name if name else "Anonymous Citizen"
        citizen_contact = contact if contact else "Not provided"

        # Save to SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints (
                complaint_id, name, contact, issue_type, description,
                image_path, latitude, longitude, location,
                confidence, severity, priority, department, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_id,
            citizen_name,
            citizen_contact,
            ai_result["issue"],
            description,
            filename,
            latitude,
            longitude,
            location,
            ai_result["confidence_val"],
            ai_result["severity"],
            ai_result["priority_val"],
            ai_result["department"],
            "Reported",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

        flash(f"Complaint successfully logged with ID {complaint_id}!", "success")
        return redirect(url_for("result", complaint_id=complaint_id))

    return render_template("report.html")


@app.route("/result/<complaint_id>")
def result(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
    complaint = cursor.fetchone()
    conn.close()

    if not complaint:
        flash(f"Complaint ID '{complaint_id}' was not found in our system.", "error")
        return redirect(url_for("track"))

    return render_template("result.html", complaint=complaint)


STATUS_ORDER = ["Reported", "Verified", "Assigned", "In Progress", "Resolved"]


@app.route("/track")
def track():
    complaint_id = request.args.get("id", "").strip().upper()
    complaint = None
    not_found = False
    current_idx = 0

    if complaint_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
        complaint = cursor.fetchone()
        conn.close()

        if not complaint:
            not_found = True
        else:
            status = complaint["status"]
            try:
                current_idx = next(i for i, s in enumerate(STATUS_ORDER) if s.lower() == status.lower())
            except StopIteration:
                current_idx = 0

    return render_template(
        "track.html",
        complaint_id=complaint_id,
        complaint=complaint,
        not_found=not_found,
        current_idx=current_idx,
        status_order=STATUS_ORDER
    )


@app.route("/api/complaints/<complaint_id>")
def get_complaint_api(complaint_id):
    """Returns single complaint details for live status polling."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id.strip().upper(),))
    complaint = cursor.fetchone()
    conn.close()

    if not complaint:
        return jsonify({"success": False, "error": "Complaint not found"}), 404

    status = complaint["status"]
    try:
        current_idx = next(i for i, s in enumerate(STATUS_ORDER) if s.lower() == status.lower())
    except StopIteration:
        current_idx = 0

    return jsonify({
        "success": True,
        "complaint_id": complaint["complaint_id"],
        "issue_type": complaint["issue_type"],
        "status": status,
        "status_idx": current_idx,
        "department": complaint["department"],
        "severity": complaint["severity"],
        "priority": complaint["priority"],
        "location": complaint["location"],
        "created_at": complaint["created_at"]
    })



# ---------------------------------------------------------
# Authentication Routes (Citizen & Admin)
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    role_hint = request.args.get("role", "citizen").lower()
    next_url = request.args.get("next", "")

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "citizen").strip().lower()

        if not identifier or not password:
            flash("Please enter your username/email and password.", "error")
            return redirect(url_for("login", role=role, next=next_url))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE (username = ? OR email = ?) AND password = ?
        """, (identifier, identifier, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Check role compatibility if attempting admin login
            if role == "admin" and user["role"] != "admin":
                flash("This account does not have municipal administrator privileges.", "error")
                return redirect(url_for("login", role="admin", next=next_url))

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]
            session["department"] = user["department"]
            session["email"] = user["email"]
            session["phone"] = user["phone"]

            flash(f"Welcome back, {user['name']}!", "success")

            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            elif user["role"] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("my_reports"))
        else:
            flash("Invalid credentials. Please verify your login details.", "error")
            return redirect(url_for("login", role=role, next=next_url))

    return render_template("login.html", role_hint=role_hint, next_url=next_url)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    username = request.form.get("username", "").strip().lower()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "").strip()

    if not name or not username or not email or not password:
        flash("Please complete all required fields to register.", "error")
        return redirect(url_for("login", role="citizen"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if username or email exists
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        flash("Username or Email already registered. Please log in.", "error")
        return redirect(url_for("login", role="citizen"))

    cursor.execute("""
        INSERT INTO users (username, email, password, name, role, department, phone)
        VALUES (?, ?, ?, ?, 'citizen', NULL, ?)
    """, (username, email, password, name, phone))
    conn.commit()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    new_user = cursor.fetchone()
    conn.close()

    session["user_id"] = new_user["id"]
    session["username"] = new_user["username"]
    session["user_name"] = new_user["name"]
    session["role"] = "citizen"
    session["department"] = None
    session["email"] = new_user["email"]
    session["phone"] = new_user["phone"]

    flash(f"Welcome to Civisense, {name}! Your citizen portal is now active.", "success")
    return redirect(url_for("my_reports"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("index"))


@app.route("/my-reports")
def my_reports():
    if not session.get("user_id"):
        flash("Please sign in to view your citizen grievance portfolio.", "info")
        return redirect(url_for("login", role="citizen", next="/my-reports"))

    user_name = session.get("user_name", "")
    phone_val = session.get("phone") or "NONE"
    email_val = session.get("email") or "NONE"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM complaints
        WHERE name = ? OR contact LIKE ? OR contact LIKE ?
        ORDER BY created_at DESC
    """, (user_name, f"%{phone_val}%", f"%{email_val}%"))
    citizen_complaints = cursor.fetchall()
    conn.close()

    return render_template(
        "my_reports.html",
        complaints=citizen_complaints,
        total_filed=len(citizen_complaints)
    )


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        flash("Municipal administrative credentials required. Please login with your officer account.", "info")
        return redirect(url_for("login", role="admin", next="/admin"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # KPI Statistics
    cursor.execute("SELECT COUNT(*) as total FROM complaints")
    total_count = cursor.fetchone()["total"]


    cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status = 'Resolved'")
    resolved_count = cursor.fetchone()["resolved"]

    cursor.execute("SELECT COUNT(*) as pending FROM complaints WHERE status != 'Resolved'")
    pending_count = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) as high_priority FROM complaints WHERE priority >= 8 OR severity IN ('HIGH', 'CRITICAL')")
    high_priority_count = cursor.fetchone()["high_priority"]

    # All complaints ordered latest first
    cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC")
    complaints = cursor.fetchall()
    conn.close()

    # Dynamic AI insights
    insights = calculate_ai_insights(complaints)

    return render_template(
        "admin.html",
        total_count=total_count,
        resolved_count=resolved_count,
        pending_count=pending_count,
        high_priority_count=high_priority_count,
        complaints=complaints,
        insights=insights
    )


# ---------------------------------------------------------
# REST APIs for Dynamic UI (Charts, Maps, AJAX Status Updates)
# ---------------------------------------------------------

@app.route("/api/admin/update-status", methods=["POST"])
def update_status():
    """Allows administrators to transition complaints across lifecycle states."""
    data = request.get_json() or {}
    complaint_id = data.get("complaint_id")
    new_status = data.get("status")

    valid_statuses = ["Reported", "Verified", "Assigned", "In Progress", "Resolved"]
    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": "Invalid status value."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM complaints WHERE complaint_id = ?", (complaint_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Complaint not found."}), 404

    cursor.execute("UPDATE complaints SET status = ? WHERE complaint_id = ?", (new_status, complaint_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "complaint_id": complaint_id,
        "new_status": new_status,
        "message": f"Complaint {complaint_id} status updated to {new_status}."
    })


@app.route("/api/analytics")
def analytics_data():
    """Returns aggregated data formatted specifically for Chart.js renders."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Category breakdown
    cursor.execute("""
        SELECT issue_type, COUNT(*) as count
        FROM complaints
        GROUP BY issue_type
        ORDER BY count DESC
    """)
    category_rows = cursor.fetchall()
    categories = {row["issue_type"]: row["count"] for row in category_rows}

    # Status breakdown
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM complaints
        GROUP BY status
    """)
    status_rows = cursor.fetchall()
    statuses = {row["status"]: row["count"] for row in status_rows}

    # Priority distribution (Low: 1-4, Medium: 5-7, High: 8-10)
    cursor.execute("""
        SELECT
            SUM(CASE WHEN priority <= 4 THEN 1 ELSE 0 END) as low,
            SUM(CASE WHEN priority BETWEEN 5 AND 7 THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN priority >= 8 THEN 1 ELSE 0 END) as high
        FROM complaints
    """)
    pri_row = cursor.fetchone()

    conn.close()

    return jsonify({
        "categories": {
            "labels": list(categories.keys()),
            "data": list(categories.values())
        },
        "statuses": {
            "labels": ["Reported", "Verified", "Assigned", "In Progress", "Resolved"],
            "data": [
                statuses.get("Reported", 0),
                statuses.get("Verified", 0),
                statuses.get("Assigned", 0),
                statuses.get("In Progress", 0),
                statuses.get("Resolved", 0)
            ]
        },
        "priorities": {
            "labels": ["Low Priority (1-4)", "Medium Priority (5-7)", "High Priority (8-10)"],
            "data": [
                pri_row["low"] or 0,
                pri_row["medium"] or 0,
                pri_row["high"] or 0
            ]
        }
    })


@app.route("/api/map-data")
def map_data():
    """Returns all complaint coordinates and metadata for the Leaflet interactive map."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT complaint_id, issue_type, location, latitude, longitude,
               severity, priority, department, status, created_at
        FROM complaints
    """)
    rows = cursor.fetchall()
    conn.close()

    markers = []
    for r in rows:
        markers.append({
            "complaint_id": r["complaint_id"],
            "issue": r["issue_type"],
            "location": r["location"],
            "lat": r["latitude"],
            "lng": r["longitude"],
            "severity": r["severity"],
            "priority": r["priority"],
            "department": r["department"],
            "status": r["status"],
            "date": r["created_at"]
        })

    return jsonify({"complaints": markers})


# ---------------------------------------------------------
# Custom Error Handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "track.html",
        complaint_id=None,
        complaint=None,
        not_found=False,
        error_message="The requested page was not found. Please navigate back to home."
    ), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected server error occurred. Please try again or check the terminal log."
    }), 500


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 60)
    print("[+] Civisense Server Starting...")
    print("[+] Local URL: http://127.0.0.1:5000")
    print("[+] Database:  SQLite initialized at database.db")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

