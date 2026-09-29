# TrustLens

TrustLens is a hybrid browser extension and analytics dashboard designed to detect deceptive user interfaces, privacy risks, dark patterns, subscription traps, and financial manipulation on webpages in real time. It features a rule-based lexical engine combined with a machine learning classification backend, operating in Local, Cloud, and Hybrid analysis modes.

---

## System Architecture

TrustLens is structured into three main layers:
1. **Chrome Extension (Frontend/Client):** Interacts with user webpages via content scripts, runs offline lexical rules and JS-based Logistic Regression models, and communicates with the backend for Cloud/Hybrid analysis.
2. **FastAPI Backend Services:** Implements advanced ML classifier inference using a pre-trained scikit-learn model, coordinates lexical rule verification in Python, hashes URLs for privacy, and logs scanning analytics.
3. **PostgreSQL Database:** Stores anonymized scan histories, guest user settings, user rating feedback, and AI model version details.

```
       +-------------------------------------------------------------+
       |                        Chrome Browser                       |
       |                                                             |
       |  +--------------------+             +--------------------+  |
       |  |  Content Script    |             |  Extension Popup   |  |
       |  |  - Extract Text    |<----------->|  - Local/Cloud Mode|  |
       |  |  - Highlight DOM   |             |  - Feedback Form   |  |
       |  +--------------------+             +---------+----------+  |
       +-----------------------------------------------|-------------+
                                                       | HTTP APIs
                                                       v
       +-------------------------------------------------------------+
       |                       FastAPI Backend                       |
       |                                                             |
       |   +--------------------+             +------------------+   |
       |   |  /api/scan Routing |             |  /api/stats/feed |   |
       |   |  - Rule Matching   |             |  - Dashboard KPIs|   |
       |   |  - ML Inference    |             |  - Feedback Log  |   |
       |   +---------+----------+             +--------+---------+   |
       +-------------|---------------------------------|-------------+
                     | SQLAlchemy                      | SQLAlchemy
                     v                                 v
       +-------------------------------------------------------------+
       |                     PostgreSQL Database                     |
       +-------------------------------------------------------------+
```

---

## Features & Modes

### 1. Analysis Modes
* **Local Mode (Offline-first):** Executes lexical dark pattern rules and a client-side TypeScript ML model locally. Doesn't contact any server, maintaining full offline operation.
* **Cloud Mode (Server-first):** Transmits page details to the FastAPI backend, executing rule comparisons and Python ML classifier model calculations.
* **Hybrid Mode (Dual engine):** Runs both local and cloud scanners concurrently. Compares results and highlights discrepancies in the popup UI if the local and cloud risk labels diverge.

### 2. User Feedback Pipeline
When scanning is finished, users can rate prediction accuracy:
* **👍 Yes (Correct classification):** Logs a positive validation check.
* **👎 No (Wrong classification):** Logs a caution rating along with optional user comments.
* Local scans will automatically log metadata to the database before recording feedback ratings.

### 3. Admin Analytics Dashboard
A standalone React SPA displaying:
* **KPI Metrics:** Total scan transaction volume, average risk scores, count of safe/risky pages.
* **Charts:** Risk distribution (Doughnut), Scan frequency over the past week (Line), and Deceptive categories breakdown (Bar).
* **Audit Tables:** History logs of recent scans, matched keywords, and user accuracy ratings.

---

## Project Structure

```
TrustLens/
├── admin/                    # Standalone React Admin Dashboard
│   ├── src/
│   │   ├── App.tsx           # Dashboard dashboard panels & Chart.js views
│   │   ├── main.tsx
│   │   └── index.css         # Styling system sheet
│   ├── package.json          # Dependencies
│   └── index.html
├── backend/                  # FastAPI Web Backend Services
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py  # /scan, /feedback, /model, /stats routers
│   │   ├── database/
│   │   │   └── connection.py # ORM engine pool & SQLite fallback configurations
│   │   ├── models/
│   │   │   └── models.py     # Users, ScanHistory, Feedback, ModelInfo tables
│   │   ├── schemas/
│   │   │   └── schemas.py    # Request/Response Pydantic validation wrappers
│   │   ├── services/
│   │   │   ├── rules_service.py # Python rule-based Lexical scanner
│   │   │   └── ml_service.py # Vectorization & scikit-learn model inference
│   │   ├── ml/               # Serialized ML parameters & version metadata
│   │   │   ├── best_model.pkl
│   │   │   ├── tfidf.pkl
│   │   │   └── modelInfo.json
│   │   └── main.py           # Core initialization & CORS configuration
│   └── requirements.txt      # Python dependencies
├── ml/                       # Offline Machine Learning scripts
│   ├── data/                 # Datasets
│   └── scripts/              # Generate & train routines
├── public/                   # Static extension assets
└── src/                      # Chrome Extension Source
    ├── background/           # Background service worker
    ├── content/              # Extractor & Highlighter
    ├── ml/                   # Offline JS model inference files
    ├── popup/                # Popup interface layouts
    └── shared/               # Universal TS interfaces
```

---

## Installation & Running

### Prerequisites
* Node.js (v18+) & npm
* Python (3.8+)
* PostgreSQL Database (optional fallback to SQLite exists)

### 1. Set Up and Run FastAPI Backend
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Install Python packages:
   ```sh
   pip install -r requirements.txt
   ```
3. (Optional) Configure database URL environment variable:
   ```sh
   # Windows PowerShell
   $env:DATABASE_URL="postgresql://username:password@localhost:5432/databasename"
   $env:DEBUG_MODE="False"
   ```
   *If no `DATABASE_URL` is set, the app will connect to PostgreSQL default or fallback to SQLite `sqlite:///./trustlens.db`.*
4. Start the server using uvicorn:
   ```sh
   python -m uvicorn app.main:app --reload --port 8000
   ```
   *Verify API works by opening `http://localhost:8000/docs` in your browser.*

### 2. Set Up and Run Extension
1. From the root directory, install npm packages:
   ```sh
   npm install
   ```
2. Build the extension:
   ```sh
   npm run build
   ```
3. Load in Google Chrome:
   - Open `chrome://extensions/`
   - Enable **Developer mode** (top-right toggle).
   - Click **Load unpacked** (top-left button).
   - Select the `dist/` directory.

### 3. Set Up and Run Admin Dashboard
1. Navigate to the admin directory:
   ```sh
   cd admin
   ```
2. Install packages:
   ```sh
   npm install
   ```
3. Start Vite developer server:
   ```sh
   npm run dev
   ```
4. Access the dashboard at `http://localhost:5173`.
