# Civisense – Smart Civic Issue Reporting & Tracking System
### *Next-Generation Autonomous Municipal Grievance & SLA Dispatch Platform*

> **Built for Hackathon Excellence & Smart City Governance**  
> **Tagline:** Report. Track. Improve.  
> **Pilot City:** Nagpur, Maharashtra (Wards 4, 7, 12, Civil Lines, Sadar, Manish Nagar)

---

## 🌟 1. Project Overview

**Civisense** is a complete, working hackathon MVP designed to bridge the gap between citizens and municipal authorities. When civic infrastructure fails—whether through dangerous road craters, burning garbage dumps, broken streetlights, or burst water mains—citizens often face clunky grievance portals with no transparency.

Civisense solves this by combining:
1. **Frictionless Citizen Reporting:** Drag-and-drop photographic evidence with one-touch GPS geolocation pinning.
2. **Autonomous Multi-Modal AI Engine:** Immediately analyzes pixel features (edges, contrast, color distributions) and natural language descriptions to classify defect types, estimate severity (Low / Med / High / Critical), calibrate a 1-to-10 priority score, and route directly to the responsible municipal department.
3. **Transparent 5-Stage Tracking:** Gives citizens live visibility (`Reported` → `Verified` → `Assigned` → `In Progress` → `Resolved`).
4. **Interactive Operations Command Center:** Empowers city administrators with real-time geospatial Leaflet heatmaps, Chart.js analytics, dynamic AI insight alerts, and one-click SLA status updates that sync instantly to citizen devices.

---

## 🚀 2. Key Features

- **⚡ Instant AI Classification:** Classifies Potholes, Garbage Dumps, Water Pipe Leaks, Broken Streetlights, Road Damage, and Overflowing Drains.
- **🎯 Dynamic SLA Urgency & Routing:** Automatically determines urgency and routes tickets to:
  - Road Maintenance Department
  - Solid Waste Management Department
  - Water Supply & Sewerage Board
  - Electrical & Public Lighting Department
  - Public Works Department (PWD)
  - Municipal Drainage & Sanitation Department
- **📍 Precise Geolocation with Map Pinning:** One-click HTML5 geolocation with fallback to Nagpur hotspot presets (Ward 12, Ward 7, Ward 4, Civil Lines, Sadar, Manish Nagar) and interactive Leaflet map pin dragging.
- **📊 Interactive Operations Command Center:**
  - Real-time KPI counters (Total, Resolved, Pending, High Priority).
  - Dynamic AI predictive insights (e.g. Ward hotspot surge detection, rapid asphalt deployment alerts).
  - Interactive Leaflet.js map with priority-colored pins (🔴 Red = High, 🟠 Amber = Medium, 🟢 Green = Low).
  - 3 dynamic Chart.js visualizations (Category breakdown, Status funnel, Priority distribution).
  - Instant in-line AJAX status changer without requiring full page reload.
- **📱 Responsive & Accessible UI:** Designed with modern civic-tech aesthetics, Plus Jakarta Sans typography, dark slate accents, vivid emerald branding, and glassmorphism cards.

---

## 🛠️ 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3 (Flask 3.x) | REST API routing, database transactions, image upload handling |
| **AI / ML Engine** | Multi-Modal Vision & Heuristic (`model/classifier.py`) | Image feature analysis (Pillow/PIL), NLP keyword extraction, priority matrix |
| **Database** | SQLite 3 (`database.db`) | Local persistence, auto-schema migration, pre-seeded complaints |
| **Geospatial Mapping** | Leaflet.js & OpenStreetMap | Interactive location picker, citizen issue map, admin ward heatmaps |
| **Data Visualizations** | Chart.js 4.x | Real-time category doughnut, status bar, and priority distribution charts |
| **Frontend UI** | HTML5, Modern Vanilla CSS3, Vanilla JS | Responsive grid, micro-animations, glassmorphism, toast notifications |
| **Icons & Typography** | FontAwesome 6, Google Fonts | Plus Jakarta Sans typography and civic-tech iconography |

---

## 📂 4. Project Structure

```
civisence_project/
│
├── app.py                     # Flask application entry point, DB init, API endpoints
├── database.db                # SQLite database (auto-created and pre-seeded on startup)
├── requirements.txt           # Python package dependencies (Flask, Pillow, Werkzeug)
├── setup_sample_images.py     # Generator for rich demo photo evidence banners
│
├── model/
│   ├── __init__.py            # Model package export
│   └── classifier.py          # AI multi-modal inference engine & department router
│
├── templates/
│   ├── base.html              # Shared layout, navigation, flash toasts, and footer
│   ├── index.html             # Landing page with hero, live metrics, and civic cards
│   ├── report.html            # Citizen issue filing form with drag-and-drop & mini-map
│   ├── result.html            # AI diagnostic confirmation card and tracking shortcut
│   ├── track.html             # Real-time citizen tracker with 5-stage visual progress timeline
│   └── admin.html             # Command Center: KPI cards, AI insights, charts, map, table
│
├── static/
│   ├── css/
│   │   └── style.css          # Premium modern civic-tech design system
│   ├── js/
│   │   └── script.js          # Leaflet maps, Chart.js, geolocation, and AJAX status sync
│   └── uploads/               # Uploaded complaint images & curated sample evidence photos
│
└── README.md                  # Complete project documentation & presentation guide
```

---

## 💻 5. Installation & Setup

Running Civisense locally takes less than 60 seconds.

### Step 1: Clone or Navigate to Directory
```bash
cd civisence_project
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Open in Your Browser
Visit:
```
http://127.0.0.1:5000
```

> **Note:** On first startup, `app.py` automatically initializes `database.db` and populates 8 realistic demo complaints across Nagpur municipal wards.

---

## 🧠 6. How the AI Component Works

### Current MVP Implementation (Multi-Modal Hybrid Engine)
In this hackathon prototype, `model/classifier.py` runs a multi-modal inference pipeline:
1. **Computer Vision Inspection (`Pillow`):**
   - Resizes image and evaluates luminance distribution, contrast standard deviation, and edge density via Laplacian filters.
   - Asphalt cracks and deep craters exhibit high edge variance and dark luminance.
   - Streetlight failures at night exhibit low overall luminance.
   - Water bursts and overflowing gutters exhibit fluid reflectance indices.
2. **Semantic Context Analysis:**
   - Scans the citizen's incident description for critical hazard indicators (e.g. *"accident"*, *"deep crater"*, *"pipe burst"*, *"choked drain"*, *"foul odor"*).
3. **Severity & Priority Score Synthesis:**
   - Combines the signals to return:
     - **Issue Classification:** E.g., `Pothole`
     - **Confidence Score:** E.g., `94%`
     - **Severity Level:** `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`
     - **Municipal Priority Rating:** `1/10` to `10/10`
     - **Recommended Department:** E.g., `Road Maintenance Department`

### 🔄 Production AI Roadmap
In a scaled production deployment:
- The rule-based heuristic can be replaced with a **fine-tuned YOLOv8 object detection model** or a **MobileNetV2 / EfficientNet transfer-learning classifier** trained on public civic datasets (such as the *Road Damage Dataset RDD2022* and *WasteNet*).
- An LLM-based agent (e.g. Gemini 1.5 Flash via Vertex AI / Google GenAI SDK) can extract audio voice notes from vernacular languages (Hindi, Marathi, etc.) into structured complaint metadata.

---

## 🗄️ 7. Database Structure (SQLite)

The database schema (`database.db`) consists of the `complaints` table:

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Internal auto-increment row index |
| `complaint_id` | TEXT UNIQUE | Citizen reference code (e.g. `CIV-10482`) |
| `name` | TEXT | Citizen full name or "Anonymous Citizen" |
| `contact` | TEXT | Phone or email address for SLA alerts |
| `issue_type` | TEXT | E.g., `Pothole`, `Garbage Dump`, `Water Leakage` |
| `description` | TEXT | Description logged by citizen |
| `image_path` | TEXT | Filename in `static/uploads/` |
| `latitude` | REAL | Decimal GPS latitude (e.g. `21.1120`) |
| `longitude` | REAL | Decimal GPS longitude (e.g. `79.0515`) |
| `location` | TEXT | Text description of Ward / landmark |
| `confidence` | INTEGER | AI confidence percentage (e.g. `94`) |
| `severity` | TEXT | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `priority` | INTEGER | Urgency score from 1 to 10 |
| `department` | TEXT | Target municipal department |
| `status` | TEXT | `Reported`, `Verified`, `Assigned`, `In Progress`, `Resolved` |
| `created_at` | TIMESTAMP | Submission timestamp |

---

## 🎬 8. Hackathon Demo Script & Walkthrough

Follow this step-by-step presentation script to showcase the full end-to-end functionality:

1. **Landing Page (`/`):**
   - Highlight the modern civic-tech UI, live statistics counters, and civic issue cards.
   - Point out the Nagpur municipal pilot badge and the quick complaint lookup bar.
2. **Report Issue Page (`/report`):**
   - Click **"Report an Issue"**.
   - Drag & drop a photo (or select a file). Observe the instant photo preview.
   - Enter description: *"Deep crater pothole causing heavy traffic skid near Ward 12 junction."* (or click a quick template chip).
   - Click **"Use Current Location"** or select the **Ward 12 (Ring Rd)** demo chip. Note how the mini Leaflet map automatically centers and updates coordinates.
   - Click **"Submit & Run AI Analysis"**.
3. **AI Result Page (`/result/<complaint_id>`):**
   - Observe the instant generation of the unique ID (e.g. `CIV-92841`).
   - Highlight the AI Vision Diagnostic Report: **Issue: Pothole**, **Confidence: 94%**, **Severity: HIGH**, **Priority: 8/10**, **Department: Road Maintenance Department**.
   - Click **"Track This Complaint"**.
4. **Live Citizen Tracker (`/track?id=CIV-XXXXX`):**
   - Point out the interactive 5-stage timeline where **Stage 1 (Reported)** is highlighted.
   - View the incident map and captured photographic evidence.
5. **Admin Operations Command Center (`/admin`):**
   - Navigate to `/admin`.
   - Show the 4 KPI counters, dynamic AI insights (*"Pothole complaints represent 38% of civic logs"*, *"Ward 12 recorded highest frequency"*).
   - Explore the **Civic Issue Geospatial Heatmap** (Leaflet) with priority-colored pins.
   - View the 3 **Chart.js** graphs (Category, Status, Priority).
   - In the complaints table, locate the new complaint and change its status from **`Reported` → `Assigned` → `In Progress` → `Resolved`**.
   - Notice the toast confirmation and how the KPI numbers adjust in real time without refreshing.
6. **Verify Real-Time Synchronization (`/track`):**
   - Return to `/track?id=CIV-XXXXX`.
   - Observe that the visual 5-stage timeline has dynamically updated to show the new status!

---

## 🔮 9. Future Enhancements

- **Autonomous Drone Verification:** Periodic drone flyovers along high-frequency pothole corridors cross-verifying repair completion.
- **Multilingual WhatsApp / Telegram Chatbot:** Allow citizens to send photos and location pins via WhatsApp Business API for instant ticket logging.
- **Predictive Monsoon Maintenance:** Time-series forecasting to preemptively clean stormwater drains before heavy rainfall events.
- **Contractor Accountability & Blockchain Audit Log:** Cryptographic proofs of work before municipal fund disbursement.

---

## 🏆 Summary

Civisense demonstrates how artificial intelligence and transparent citizen engagement can transform municipal governance from reactive paperwork into rapid, data-driven action.
