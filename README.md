# CSTAN – Citizen Safety & Travel Assistance Network
### AI-Enabled Citizen & Tourist Safety Platform

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![AI/ML](https://img.shields.io/badge/AI%2FML-Scikit--Learn%20%7C%20IsolationForest-orange.svg)](https://scikit-learn.org/)
[![GIS](https://img.shields.io/badge/GIS-Leaflet.js%201.9-green.svg)](https://leafletjs.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-Passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **One-Line Summary**: CSTAN is an AI-enabled citizen and tourist safety platform that integrates digital identity, real-time geofencing, emergency SOS, location-based assistance, anomaly detection, and centralized authority monitoring into a single unified system.

---

## 🌟 Key Features

1. **Digital Tourist/Citizen Identity (Pass)**
   - Unique generated Digital Safety Pass (`CSTAN-TN-2026-XXXX`).
   - Secure verification token and QR stamp.
   - Encrypted emergency contacts, blood group, and medical notes.

2. **Dynamic Safety Score Engine**
   - Real-time rating from 0 to 100 with clear risk classifications:
     - **80 – 100**: *Low Risk - Safe* (Green)
     - **55 – 79**: *Moderate Risk - Caution* (Amber)
     - **< 55**: *High Risk - Alert* (Red)
   - Factors evaluated: Geofence boundaries, proximity to active incidents, time of day (night travel), and active distress signals.

3. **Geofencing & Proximity Warnings**
   - Precise distance calculations via the Haversine formula.
   - Classifications: **Safe Haven (Green)**, **Caution Zone (Amber)**, **Restricted/Prohibited Zone (Red)**.
   - Instant visual and audio alarms when approaching or entering hazardous boundaries.

4. **One-Touch Emergency SOS Dispatch**
   - Categories: *Medical Emergency, Accident, Lost Person, Harassment, Security Threat, Other*.
   - Live location capture with immediate transmission to Central Command and emergency contacts.
   - Response pipeline tracking: `NEW` $\rightarrow$ `ACKNOWLEDGED` $\rightarrow$ `IN PROGRESS` $\rightarrow$ `RESOLVED`.

5. **AI/ML Anomaly Detection**
   - Evaluates speed, distance deltas, and kinematics using Scikit-Learn `IsolationForest`.
   - Identifies prolonged inactivity in high-risk zones and sudden trajectory divergence.

6. **Interactive GIS Map & Route Simulator**
   - Live Leaflet.js interactive maps with custom emergency services markers (Police, Hospitals, Fire, Tourist Desks).
   - Built-in **"Simulate Walk Route"** feature allowing effortless hackathon/college demonstrations without leaving the room.
   - HTML5 Geolocation API integration for real GPS tracking.

7. **Multilingual Localization**
   - Instant on-the-fly switching across 6 languages:
     - **English**
     - **Tamil (தமிழ்)**
     - **Hindi (हिन्दी)**
     - **Telugu (తెలుగు)**
     - **Malayalam (മലയാളം)**
     - **Kannada (ಕನ್ನಡ)**

8. **Authority Central Command & Triage Console**
   - Live GIS map tracking all registered tourists and emergency beacons.
   - Incident triage management with disposition logs and one-click status transitions.
   - Real-time Geofence boundary creator and city-wide advisory broadcast tool.

---

## 🏗️ System Architecture

```text
               ┌────────────────────────────────────────────────────────┐
               │              CSTAN Web & Mobile Interface              │
               │  (HTML5 • CSS3 • Leaflet.js • Bootstrap • i18n Engine)  │
               └───────────────────────────┬────────────────────────────┘
                                           │  REST APIs / JSON
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                    Flask Backend Core                  │
               │                 (Authentication & Routes)              │
               └─────────┬───────────────────┬────────────────────┬─────┘
                         │                   │                    │
                         ▼                   ▼                    ▼
               ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐
               │  Safety Engine   │ │ Anomaly Detector │ │ Location Hub   │
               │ (Haversine &     │ │ (IsolationForest │ │ (Nearby Hubs & │
               │  Dynamic Score)  │ │  & Kinematics)   │ │  Geofencing)   │
               └─────────┬────────┘ └────────┬─────────┘ └────────┬───────┘
                         │                   │                    │
                         └───────────────────┼────────────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     SQLite Database       │
                               │ (SQLAlchemy ORM Entities) │
                               └───────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Option A: 1-Click Launch (Recommended for Windows / Linux / Mac)
- **Windows**: Double-click [`run.bat`](file:///c:/Users/prade/OneDrive/Desktop/Oct/01.10.2026/run.bat)
- **Linux / macOS**: Run `./run.sh`

### Option B: Standard Manual Setup
1. **Clone & enter directory**:
   ```bash
   git clone https://github.com/<your-username>/cstan.git
   cd cstan
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize and seed database**:
   ```bash
   python seed_data.py
   ```
4. **Run Application**:
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:5000`

### Option C: Docker & Docker Compose
Run the entire platform inside an isolated container with zero host installation:
```bash
docker compose up --build
```
Access at `http://localhost:5000`.

### Option D: Cloud Deployment (Render / Railway / Heroku)
- **Render**: Connect repository; uses `render.yaml` automatically.
- **Heroku / Railway**: Uses the included `Procfile` (`web: gunicorn wsgi:app`).
- Set environment variables as demonstrated in [`.env.example`](file:///c:/Users/prade/OneDrive/Desktop/Oct/01.10.2026/.env.example).

---

## 🔑 Demo Credentials

| Role | Email | Password | Features Accessible |
| :--- | :--- | :--- | :--- |
| **Citizen / Tourist** | `tourist@cstan.org` | `password123` | Live Map, Route Simulation, Emergency SOS, Digital Pass, Multi-language UI |
| **Authority Admin** | `admin@cstan.org` | `admin123` | GIS Incident Map, SOS Dispatch Triage, Geofence Creator, Advisory Broadcast |

*(Both login cards feature 1-click auto-fill buttons on the login screen for instant demonstration).*

---

## 🧪 Running Automated Tests

Run the comprehensive unit and integration test suite:
```bash
python tests/test_cstan.py
```

---

## 📁 Project Structure

```
01.10.2026/
├── app.py                   # Main Flask application & API routes
├── models.py                # SQLAlchemy database models
├── safety_engine.py         # Haversine distance, geofencing & AI anomaly engine
├── seed_data.py             # Database initialization with realistic seed data
├── templates/
│   ├── base.html            # Core layout with navbar, language selector & footer
│   ├── login.html           # Login page with 1-click demo credential presets
│   ├── register.html        # Registration with auto-generated Digital ID
│   ├── user_dashboard.html  # Citizen hub (Map, SOS, Score gauge, Services)
│   ├── admin_dashboard.html # Command console (GIS Map, SOS Triage, Geofences)
│   └── profile.html         # Digital Safety Pass card & emergency history
├── static/
│   ├── css/style.css        # Modern safety-themed CSS stylesheet
│   └── js/
│       ├── translations.js  # 6-language dictionary (EN, TA, HI, TE, ML, KN)
│       ├── map_engine.js    # Client Leaflet map, geofencing & simulation
│       └── admin_map.js     # Admin GIS telemetry and triage handler
├── tests/
│   ├── __init__.py
│   └── test_cstan.py        # Complete automated test suite
├── PROJECT_DOCUMENTATION.md # Detailed academic/hackathon report
└── README.md                # Project documentation & setup instructions
```

---

## 🎓 Academic / Hackathon Presentation Tips
1. **Show the Digital Safety Pass**: Highlight how each tourist gets an encrypted pass with emergency contact details and blood group.
2. **Demonstrate Multilingual Support**: Use the language dropdown at the top right to switch into Tamil, Hindi, or Telugu—watch all headings and alerts change instantly.
3. **Run the Walk Simulation**: Click `Simulate Walk Route` on the user map. Observe the live score update as the tourist enters caution and restricted zones.
4. **Trigger SOS**: Click the big red SOS button, pick "Medical Emergency", and submit.
5. **Demonstrate Admin Command Console**: Open `/admin`, show the live beacon on the GIS map, inspect the coordinates, and advance the status from `ACKNOWLEDGED` to `RESOLVED`.
