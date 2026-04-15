# Trade Reconciliation Service

A full-stack web application built to ingest, compare, and report discrepancies between two trade datasets.

## 📊 Discrepancy Seeding

[cite_start]As required, this repository documents the exact count of each discrepancy type seeded. Out of a base dataset of 50 trades, I introduced exactly **10 discrepancies**:

- [cite_start]**Price Mismatches (3):** Trade IDs `5`, `25`, `48`
- [cite_start]**Quantity Mismatches (2):** Trade IDs `12`, `40`
- [cite_start]**Status Mismatches (3):** Trade IDs `18`, `33`, `45`
- [cite_start]**Missing Trades (2):**
  - Trade ID `51` (**MISSING_EXTERNAL**: Exists in internal, missing in external)
  - Trade ID `52` (**MISSING_INTERNAL**: Exists in external, missing in internal)

---

## 🚀 How to Run the Service Locally

[cite_start]Below are the instructions detailing how to run the service locally. You will need Python 3.9+ and Node.js 18+.

### 1. Start the Backend (API & Database)

Open a terminal in the root directory:

```bash
cd backend
python -m venv venv

# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

pip install -r requirements.txt
python run.py

---

The Flask API will run on http://127.0.0.1:5000. The SQLite database is automatically initialized.

2. Start the Frontend (UI)
Open a second terminal in the root directory:

Bash
cd frontend
npm install
npm run dev
The React application will run on http://localhost:5173. Open this URL in your browser to trigger a reconciliation run.

🧪 How to Run the Tests
Below are the instructions on how to run the tests.

With your backend virtual environment activated, run:

Bash
python -m pytest backend/tests/ -v
(Note: The test suite uses an isolated, in-memory SQLite database to ensure tests are fast and do not corrupt your local data).

🤔 Assumptions Made
The following section outlines any assumptions made during development:

Ambiguity in "Missing" Definitions: I assumed MISSING_INTERNAL means the trade was found in the external file but not the internal file, and MISSING_EXTERNAL means it was found in the internal file but not the external file.

Malformed Data Handling: If a row is missing a critical numeric field (like price or quantity), I assumed it should not default to 0. Instead, the ingestion engine logs a warning and skips the row entirely.

Reconciliation Engine Execution: Given the required scale (50-100 rows), I assumed performing the comparison in-memory using Python dictionaries was the optimal approach for readability.

⚠️ Known Limitations
The following are known limitations and considerations for real-world scaling:

Synchronous Processing: Currently, the run endpoint blocks the HTTP thread while reading files and computing breaks. For large datasets, this must be decoupled using a message broker (e.g., RabbitMQ/Kafka) and background workers (e.g., Celery).

Database Migration: Moving from SQLite to a robust RDBMS like PostgreSQL is necessary for production environments.

Database-Level Reconciliation: Instead of pulling rows into application memory, the comparison engine would need to be rewritten to leverage native SQL JOINs, executing the logic entirely within the database layer for maximum performance.
```
