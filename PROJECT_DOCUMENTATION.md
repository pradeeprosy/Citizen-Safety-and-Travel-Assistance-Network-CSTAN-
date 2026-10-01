# PROJECT DOCUMENTATION: CSTAN
## Citizen Safety and Travel Assistance Network
### An Integrated AI-Enabled Public Safety and Tourist Guidance Platform

---

## 1. Executive Abstract

**CSTAN (Citizen Safety and Travel Assistance Network)** is a smart, integrated digital platform developed to elevate the security, safety, and guidance infrastructure for citizens and domestic/international tourists. Traditional travel solutions remain fragmented—navigation services, municipal emergency hotlines, and tourism advisories operate as isolated silos. CSTAN resolves this gap by providing an end-to-end ecosystem combining **cryptographic digital tourist identities**, **real-time Haversine geofencing**, **dynamic heuristic safety scoring**, **one-touch GPS distress dispatch**, **machine learning anomaly detection (Isolation Forest)**, **multilingual localization across six languages**, and a **centralized administrative command console**. 

The solution enables rapid emergency intervention, transparent risk awareness, and proactive authority monitoring while strictly adhering to data privacy and security principles.

---

## 2. Problem Statement

Modern citizens and travelers navigating unfamiliar urban corridors encounter critical challenges:
1. **Disorientation in Hazardous Zones**: Tourists inadvertently stray into high-crime corridors, industrial rail yards, or active construction hazard zones without prompt warning.
2. **Emergency Response Friction**: Panic, unfamiliarity with local helpline codes (100, 108, 112), and lack of precise coordinate sharing significantly delay first responders.
3. **Linguistic Barriers**: Non-native travelers cannot comprehend local emergency advisories, street signs, or helpline directives.
4. **Decentralized Oversight**: Law enforcement and tourism departments lack unified situational awareness regarding active visitor density and ongoing distress incidents.
5. **Absence of Intelligent Movement Telemetry**: Existing systems cannot distinguish normal sightseeing strolls from erratic, distressful movement patterns or prolonged incapacitation.

---

## 3. System Architecture & High-Level Design

The CSTAN architecture follows a modular, decoupled tier model:

```
[ Client Presentation Layer ]
  - Leaflet.js GIS Interactive Cartography
  - Bootstrap 5.3 Responsive Interface
  - Multilingual Client Engine (EN, TA, HI, TE, ML, KN)
  - HTML5 Geolocation API & Synthetic Route Simulator
            │
            ▼  (JSON over HTTPS REST APIs)
[ Application & Business Logic Tier (Python / Flask) ]
  ├── Authentication & Session Guard (Flask-Login, Werkzeug)
  ├── Geofence Spatial Collision Engine (Haversine Formula)
  ├── Dynamic Safety Score Evaluator
  ├── AI Anomaly Detector (Scikit-Learn IsolationForest)
  └── Emergency SOS Dispatch & Incident Triage Pipeline
            │
            ▼  (SQLAlchemy ORM)
[ Persistence Tier ]
  └── SQLite / Relational Database (Users, Geofences, Emergencies, Logs)
```

---

## 4. Key Functional Modules

### 4.1 Digital Safety Identity Module
- Generates a tamper-evident digital credential (`CSTAN-TN-2026-XXXX`).
- Encapsulates citizen details, emergency contacts, medical notices, and blood group.
- Generates a verifiable token stamp for identity verification at tourist desks and transit police booths.

### 4.2 Geofencing & Spatial Boundary Engine
- Manages virtual circular perimeters categorized by risk profile:
  - **Safe Haven (`safe`)**: Verified tourist corridors, lit promenades, round-the-clock police booths.
  - **Caution Zone (`caution`)**: Uneven terrain, excavations, low illumination, seasonal high tides.
  - **Restricted Zone (`restricted`)**: High-security maritime basins, high-voltage yards, sensitive perimeter areas.
- Generates proactive warnings when entering or approaching within 300 meters of hazardous zones.

### 4.3 Dynamic Safety Score Engine
Evaluates real-time threat vectors and yields an intuitive safety score $S \in [10, 100]$:
$$S = 100 - \Delta_{\text{geofence}} - \Delta_{\text{alerts}} - \Delta_{\text{sos}} - \Delta_{\text{anomaly}} - \Delta_{\text{night}}$$
- Classification:
  - **80 – 100**: Low Risk (Safe)
  - **55 – 79**: Moderate Risk (Caution)
  - **10 – 54**: High Risk (Immediate Danger)

### 4.4 One-Touch Emergency SOS Dispatch
- Captures pinpoint latitude, longitude, timestamp, and emergency classification (*Medical, Accident, Lost, Harassment, Threat, Other*).
- Dispatches incidents into the Central Command Queue with a structured lifecycle:
  $$\text{NEW} \longrightarrow \text{ACKNOWLEDGED} \longrightarrow \text{IN PROGRESS} \longrightarrow \text{RESOLVED}$$

### 4.5 AI/ML Anomaly Detection
- Integrates `sklearn.ensemble.IsolationForest` trained on normative urban travel kinematics (velocity, displacement deltas, turn angles).
- Complemented by heuristic detectors identifying prolonged immobility in caution zones ($>180$ seconds) or velocity anomalies ($>140$ km/h).

### 4.6 Multilingual Support
- Built-in internationalization across **English, Tamil, Hindi, Telugu, Malayalam, and Kannada**.
- All interface elements, advisories, and emergency categories dynamically reflect the selected language.

---

## 5. Mathematical Modeling & Algorithmic Formulation

### 5.1 Great-Circle Distance (Haversine Formula)
To compute spherical geodesic distance between point $P_1(\phi_1, \lambda_1)$ and point $P_2(\phi_2, \lambda_2)$ with mean Earth radius $R = 6,371,000\text{ m}$:

$$\Delta \phi = \phi_2 - \phi_1, \quad \Delta \lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$

$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$

$$d = R \cdot c$$

A geofence boundary collision is triggered whenever $d \le r_{\text{geofence}}$.

---

## 6. Database Schema Design

| Table Name | Primary Key | Key Attributes | Purpose |
| :--- | :--- | :--- | :--- |
| `users` | `id` | `username`, `email`, `password_hash`, `role`, `digital_id`, `phone`, `emergency_contact_phone`, `blood_group` | Stores user credentials, roles, and digital passes |
| `travel_profiles` | `id` | `user_id`, `destination`, `purpose`, `start_date`, `status` | Active travel itinerary and destination logging |
| `geofences` | `id` | `name`, `latitude`, `longitude`, `radius`, `risk_level`, `advisory`, `active` | Spatial boundary definitions and risk ratings |
| `emergency_requests` | `id` | `user_id`, `type`, `latitude`, `longitude`, `status`, `severity`, `admin_notes` | SOS distress dispatches and triage history |
| `safety_alerts` | `id` | `title`, `description`, `latitude`, `longitude`, `risk_level`, `active` | Authority-broadcasted public advisories |
| `nearby_services` | `id` | `name`, `category`, `latitude`, `longitude`, `contact_number`, `is_24_7` | Emergency facilities directory (Police, Hospital, Fire) |
| `location_logs` | `id` | `user_id`, `latitude`, `longitude`, `speed`, `timestamp` | Telemetry trails for trajectory and anomaly analysis |

---

## 7. Security and Privacy Safeguards

1. **Password Security**: Strong irreversible password hashing using PBKDF2/SHA-256 via `werkzeug.security`.
2. **Role-Based Access Control (RBAC)**: Strict segregation between tourist views and administrative command endpoints (`role == 'admin'`).
3. **Data Minimization**: Coordinates are logged solely during active travel sessions and can be flushed post-journey.
4. **Integrity Verification**: Digital IDs include cryptographic hash formats preventing identity duplication or forgery.

---

## 8. Verification & Test Outcomes

A comprehensive test suite (`tests/test_cstan.py`) was executed to confirm system robustness:
- **Haversine Distance Accuracy**: Verified sub-meter geodesic accuracy for short and medium coordinate pairs.
- **Geofence Collision**: Confirmed precise transitions (`INSIDE`, `APPROACHING`, `SAFE`).
- **Dynamic Safety Scoring**: Validated mathematical clamping and deduction weights.
- **Authentication & RBAC**: Confirmed unauthorized access blocks to `/admin` endpoints.
- **SOS Triage Lifecycle**: Validated full pipeline state transitions (`NEW` $\rightarrow$ `ACKNOWLEDGED` $\rightarrow$ `IN PROGRESS` $\rightarrow$ `RESOLVED`).

---

## 9. Future Scope and Enhancements

1. **IoT & Wearable Integration**: Pairing with BLE smart wristbands to dispatch SOS upon cardiac irregularity or fall detection.
2. **Edge Computer Vision**: Ingestion of authorized traffic camera feeds to correlate anomaly detections with localized density spikes.
3. **Offline Mesh-Radio Fallback**: LoRa/Bluetooth Low Energy mesh networks allowing SOS broadcasting in cellular dead zones.
4. **Voice-Activated SOS**: On-device keyword detection ("CSTAN Help") for hands-free distress triggering.

---

## 10. Conclusion

CSTAN delivers a scalable, production-ready, AI-driven public safety solution that successfully converges traveler convenience with municipal security oversight. Its balance of real-time GIS cartography, dynamic mathematical risk scoring, multilingual accessibility, and authoritative incident triage positions it as an exemplary platform for smart city public safety initiatives, final-year engineering projects, and innovation hackathons.
