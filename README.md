# Trade Reconciliation Service

[cite_start]A full-stack web application built to ingest, compare, and report discrepancies between two trade datasets (an internal system and a prime broker's external system)[cite: 25, 31, 32].

## 🛠 Tech Stack

- [cite_start]**Backend:** Python, Flask, Pandas (for ingestion), SQLAlchemy.
- [cite_start]**Database:** SQLite (Requires zero external setup; runs entirely locally)[cite: 22, 72].
- [cite_start]**Frontend:** React, Vite, Axios[cite: 59, 64].
- [cite_start]**Testing:** Pytest (utilizing an isolated, in-memory SQLite database).

---

## 📊 Discrepancy Seeding (Test Data)

[cite_start]As requested, I generated a base dataset of 50 trades and introduced specific discrepancies into ~20% of the records[cite: 38]. The reconciliation engine successfully identifies all **10 seeded discrepancies**:

- [cite_start]**Price Mismatches (3):** Trade IDs `5`, `25`, `48` [cite: 39]
- [cite_start]**Quantity Mismatches (2):** Trade IDs `12`, `40` [cite: 40]
- [cite_start]**Status Mismatches (3):** Trade IDs `18`, `33`, `45` [cite: 41]
- [cite_start]**Missing Trades (2):** [cite: 42]
  - [cite_start]Trade ID `51` (**MISSING_EXTERNAL**: Exists in internal, missing in external) [cite: 54]
  - Trade ID `52` (**MISSING_INTERNAL**: Exists in external, missing in internal) [cite: 53]

---

## 🚀 How to Run the Service Locally

The application is split into a backend and frontend. [cite_start]You do not need to install any external databases to run this project[cite: 22].

### Prerequisites

- Python 3.9+
- Node.js 18+

### 1. Start the Backend (API & Database)

[cite_start]Open a terminal in the root directory and run the following commands to start the backend from scratch[cite: 23, 113]:

```bash
cd backend
python -m venv venv

# Activate the virtual environment:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

pip install -r requirements.txt
python run.py

---

The Flask API will run on http://127.0.0.1:5000. The SQLite database (trade_recon.db) is automatically initialized on the first run.2. Start the Frontend (UI)Open a second terminal in the root directory and run:Bashcd frontend
npm install
npm run dev
The React application will run on http://localhost:5173. Open this URL in your browser to view the reporting dashboard and trigger a reconciliation run.🧪 How to Run the TestsThe backend includes a comprehensive Pytest suite covering data ingestion (error handling), reconciliation logic (verifying exact counts of matches/breaks), and API endpoints.With your backend virtual environment activated, run the tests with a single command:Bashpython -m pytest backend/tests/ -v
(Note: The test suite uses an isolated, in-memory SQLite database via conftest.py to ensure tests are fast and do not corrupt your local data).📡 API Endpoints & Sample RequestsA test_requests.http file is included in the repository root to demonstrate the full API flow. If you use the VS Code REST Client extension, you can trigger these directly.Alternatively, you can test the endpoints manually once the backend is running:POST /reconciliation/run - Triggers ingestion and reconciliation.GET /reconciliation/runs - Lists all past runs.GET /reconciliation/runs/{run_id}/summary - Gets matched/break/missing counts.GET /reconciliation/runs/{run_id}/breaks - Gets all discrepancies.GET /reconciliation/runs/{run_id}/breaks?field=price - Filters breaks by a specific field.🤔 Assumptions MadeAmbiguity in "Missing" Definitions: I assumed MISSING_INTERNAL means the trade was found in the external file but not the internal file, and MISSING_EXTERNAL means it was found in the internal file but not the external file.Malformed Data Handling: If a row is missing a critical numeric field (like price or quantity), or contains unparseable data, I assumed it should not default to 0. Instead, the ingestion engine logs a warning and skips the row entirely, continuing with the rest of the file.Reconciliation Engine Execution: Given the required scale (50-100 rows), I assumed performing the comparison in-memory using Python dictionaries was the optimal approach for readability and speed.⚠️ Known Limitations & Real-World ScalingWhile this architecture works perfectly for the requested scope, a production environment processing millions of trades under a tight SLA would require the following changes:Asynchronous Processing: Currently, the POST /reconciliation/run endpoint blocks the HTTP thread while reading files and computing breaks. For large datasets, this must be decoupled using a message broker (e.g., RabbitMQ/Kafka) and background workers (e.g., Celery).Database Migration: Moving from SQLite to a robust RDBMS like PostgreSQL.Database-Level Reconciliation: Instead of pulling millions of rows into application memory, the comparison engine would be rewritten to leverage native SQL JOINs and CASE statements, executing the logic entirely within the database layer for maximum performance.Batch Ingestion: Data ingestion via pandas would need to be chunked to avoid memory exhaustion during the load phase.
```
