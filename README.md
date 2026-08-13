# CropChar — Crop-Residue & Fire Monitoring System

CropChar is an end-to-end crop-residue fire monitoring and unauthorized burning alert platform built for real-time agricultural compliance.

It integrates NASA FIRMS satellite thermal hotspot data, geographically matches fire points to agricultural field polygons using spatial joins, checks permit and seasonal burning regulations, tracks repeat offending fields, and presents findings on an interactive dark-themed web dashboard with automated email alert capabilities.

---

## 🏗️ System Architecture & Data Flow

```
+------------------+     +-----------------------+     +--------------------------+
| NASA FIRMS API   | --> | Spatial Join          | --> | Seasonal Permit Rules    |
| (or Fallback CSV)|     | (GeoPandas & Shapely) |     | (Field Season Window)    |
+------------------+     +-----------------------+     +--------------------------+
                                                                    |
                                                                    v
+------------------+     +-----------------------+     +--------------------------+
| Email Alert      | <-- | FastAPI Backend       | <-- | Unauthorized Detection & |
| (SMTP Notifier)  |     | (JSON Rest API)       |     | Repeat Offender Tracking |
+------------------+     +-----------------------+     +--------------------------+
                                     |
                                     v
                         +-----------------------+
                         | React + Leaflet       |
                         | Interactive Dashboard |
                         +-----------------------+
```

---

## 🚀 Key Features

1. **NASA FIRMS Thermal Fire Hotspot Integration**: Automatically queries NASA VIIRS thermal sensors for recent hotspots across configurable geographic bounding boxes.
2. **Reliable Offline Fallback**: If NASA's servers are unreachable or an API key isn't set up, CropChar seamlessly switches to a local realistic fallback dataset (`data/sample_hotspots.csv`) so the demo never breaks.
3. **GeoPandas Spatial Point-in-Polygon Matching**: Uses GIS spatial joins (`predicate="within"`) to map thermal points to exact agricultural field boundaries.
4. **Seasonal Permit Rule Engine**: Evaluates field-specific permit flags (`permitted: true/false`) and active burning season dates (`season_start`, `season_end`).
5. **Persistent Repeat Offender Logging**: Records unauthorized burn occurrences in `data/offender_log.json` to highlight high-risk fields over time.
6. **Modern React & Leaflet UI**: Displays field boundary overlays, color-coded fire status pins (🔴 Unauthorized, 🟢 Cleared), live summary metrics, and repeat offender rankings.
7. **Automated SMTP Email Alert System**: Sends immediate email alerts to compliance authorities when suspicious burns are flagged.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pandas, GeoPandas, Shapely, Requests, python-dotenv.
- **Frontend**: React 18, Leaflet, react-leaflet, Axios, Modern Vanilla CSS.
- **Data Formats**: GeoJSON (EPSG:4326), CSV, JSON.
- **External Services**: NASA FIRMS API, OpenStreetMap tile servers, SMTP Email.

---

## 📁 Project Structure

```
cropchar/
├── backend/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI endpoints & CORS configuration
│   ├── alerts/
│   │   ├── __init__.py
│   │   └── notifier.py             # SMTP email dispatch module
│   └── data_pipeline/
│       ├── __init__.py
│       ├── fetch_firms.py          # NASA FIRMS API fetch & fallback handler
│       ├── match.py                # Shapely & GeoPandas spatial join matching
│       ├── rules.py                # Seasonal permit rule evaluation engine
│       ├── offenders.py            # Persistent offender log JSON read/write
│       ├── pipeline.py             # Main end-to-end data pipeline runner
│       └── validate_boundaries.py  # GeoJSON CRS & field validation utility
├── frontend/
│   ├── package.json
│   ├── public/
│   │   ├── index.html
│   │   └── sample_boundaries.geojson
│   └── src/
│       ├── App.js                  # Main dashboard container & state logic
│       ├── Map.js                  # Leaflet interactive map component
│       ├── Sidebar.js              # Flagged burns & repeat offenders list
│       ├── StatsPanel.js           # Top statistics counters
│       ├── index.js
│       └── index.css               # Glassmorphic dark theme stylesheet
├── data/
│   ├── sample_boundaries.geojson   # Demo agricultural field polygons (EPSG:4326)
│   ├── permits_mock.csv            # Field permit status & season dates
│   ├── sample_hotspots.csv         # Realistic offline fallback fire hotspots
│   └── offender_log.json           # Offender violation count log
├── .env.example                    # Environment variable configuration template
├── .gitignore                      # Git exclusion rules
├── requirements.txt                # Python package dependencies
├── test_pipeline.py                # Automated end-to-end unit test suite
└── README.md                       # Documentation & setup guide
```

---

## ⚡ Quick Start & Setup Guide

### Step 1: Clone & Environment Setup

```bash
# Navigate into the project folder
cd cropchar

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### Step 2: Environment Variables (`.env`)

Copy `.env.example` to create `.env`:

```bash
cp .env.example .env
```

Edit `.env` (Optional for live NASA or real SMTP email sending):

```env
FIRMS_MAP_KEY=YOUR_NASA_FIRMS_MAP_KEY
EMAIL_ADDRESS=YOUR_DEMO_EMAIL@gmail.com
EMAIL_APP_PASSWORD=YOUR_GMAIL_APP_PASSWORD
ALERT_RECIPIENT=YOUR_ALERT_RECIPIENT@gmail.com
FIRMS_BBOX=78.0,10.5,78.5,11.0
FIRMS_SOURCE=VIIRS_SNPP_NRT
FIRMS_DAY_RANGE=1
```

> **Note**: If `FIRMS_MAP_KEY` is not provided or remains default, CropChar automatically runs in **Offline Fallback Mode** using `data/sample_hotspots.csv`.

---

### Step 3: Run the FastAPI Backend

```bash
uvicorn backend.api.main:app --reload
```

The backend server will start at:
- **API Base**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

Test the endpoints:
- `GET http://localhost:8000/` -> `{"status": "CropChar backend is alive"}`
- `GET http://localhost:8000/hotspots` -> Returns matched hotspots & offender counts.

---

### Step 4: Run the React Frontend

Open a new terminal window:

```bash
cd cropchar/frontend
npm install
npm start
```

The React dashboard will open automatically at:
- `http://localhost:3000`

---

## 🧪 Automated Testing

Run the full end-to-end test suite to verify pipeline execution, GeoJSON CRS validation, spatial join math, permit rules, and API endpoints:

```bash
python test_pipeline.py
```

---

## 🎭 2-Minute Demonstration Flow

1. **Launch Dashboard**: Open `http://localhost:3000`. Observe the status badge showing `DATA SOURCE: FALLBACK` (or `LIVE`).
2. **Explore Map**: See the green field polygon boundaries overlaid on the map. Notice the 🔴 red markers (Unauthorized Burns) and 🟢 green markers (Cleared/Permitted Burns).
3. **Inspect Hotspots**: Click on a red marker over **Field `field_01`**. The popup displays field owner, crop type, acquisition date, confidence level, and `🔴 Unauthorized Burn` status.
4. **Review Sidebar**: Examine the **Flagged Unauthorized Burns** list in the right sidebar. Check the **Repeat Offender Log** showing `field_01 — 3 times`.
5. **Trigger Email Alert**: Click the **`📧 Send Email Alert`** button for `field_01`. Watch the status update to confirm alert dispatch.

---

## ❓ Troubleshooting

- **`ModuleNotFoundError: No module named 'geopandas'`**: Ensure your virtual environment is active (`.\venv\Scripts\activate`) before running `uvicorn` or tests.
- **Frontend map styling missing**: Ensure `index.html` includes the Leaflet CSS `<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />`.
- **CORS Error in Browser**: FastAPI has `CORSMiddleware` configured to allow request origins from `localhost:3000`.

---

## 📜 License
Built for hackathons and educational open-source demonstration.
