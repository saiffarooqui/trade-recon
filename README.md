# Trade Reconciliation Service

A full-stack web application built to ingest, compare, and report discrepancies between two trade datasets.

## Datasets & Discrepancy Seeding

The `internal_trades.csv` and `external_trades.csv` files are present in the `backend/data` folder.

Out of a base dataset of 50 trades, I introduced exactly **10 discrepancies**:

- **Price Mismatches (3):** Trade IDs `5`, `25`, `48`
- **Quantity Mismatches (2):** Trade IDs `12`, `40`
- **Status Mismatches (3):** Trade IDs `18`, `33`, `45`
- **Missing Trades (2):**
  - Trade ID `51` (**MISSING_EXTERNAL**: Exists in internal, missing in external)
  - Trade ID `52` (**MISSING_INTERNAL**: Exists in external, missing in internal)

---

## How to Run the Service Locally

Below are the instructions detailing how to run the service locally. You will need Python 3.9+ and Node.js 18+.

### 1. Start the Backend (API & Database)

Open a terminal in the root directory:

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate.bat
# On macOS/Linux:
#source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

---

The Flask API will run on `http://127.0.0.1:5000`. The SQLite database is automatically initialized.

<hr>

### 2. Start the Frontend (UI)

Open a second terminal in the root directory:

```bash
cd frontend
npm install
npm run dev
```

The React application will run on http://localhost:5173. Open this URL in your browser to trigger a reconciliation run.

### How to Run the Tests

Below are the instructions on how to run the tests.

With your backend virtual environment activated, run:

```bash
python -m pytest backend/tests/ -v
```

(Note: The test suite uses an isolated, in-memory SQLite database to ensure tests are fast and do not corrupt your local data).

## Assumptions Made

The following section outlines any assumptions made during development:

**Ambiguity in "Missing" Definitions:** I assumed MISSING_INTERNAL means the trade was found in the external file but not the internal file, and MISSING_EXTERNAL means it was found in the internal file but not the external file.

**Malformed Data Handling:** If a row is missing a critical numeric field (like price or quantity), I assumed it should not default to 0. Instead, the ingestion engine logs a warning and skips the row entirely.

**Reconciliation Engine Execution:** Given the required scale, I assumed performing the comparison in-memory using Python dictionaries was the optimal approach for readability.

## Known Limitations

The following are known limitations and considerations for real-world scaling:

1. Database Migration: Moving from SQLite to a robust RDBMS like SQL Server/PostgreSQL is necessary for production environments.

2. Database-Level Reconciliation: Instead of pulling rows into application memory, the comparison engine would need to be rewritten to leverage native SQL JOINs, executing the logic entirely within the database layer for maximum performance.

3. Synchronous Processing: Currently, the run endpoint blocks the HTTP thread while reading files and computing breaks. For large datasets, this must be decoupled using a message broker (e.g., RabbitMQ/Kafka) and background workers (e.g., Celery).

## API Documentation

Base URL
`http://localhost:5000/reconciliation`

1. Trigger a New Reconciliation Run
   - Endpoint: `POST /reconciliation/run`
   - Description: Starts a new reconciliation run by ingesting both trade files and running the reconciliation engine.
   - Request Body: None
   - Response:
     - `201 Created`
     - JSON with reconciliation summary or error message.

2. List All Past Runs
   - Endpoint: ``GET /reconciliation/runs`
   - Description: Returns a list of all past reconciliation runs with summary counts.
   - Response:
     - `200 OK`
     - JSON array of run summaries.

3. Get Summary for a Specific Run
   - Endpoint: `GET /reconciliation/runs/<run_id>/summary`
   - Description: Returns matched, breaks, and missing counts for a specific run.
   - Response:
     - `200 OK`
     - JSON summary for the run.
     - `404 Not Found` if run does not exist.

4. Get Full Reconciliation Results
   - Endpoint: `GET /reconciliation/runs/<run_id>`
   - Description: Returns all reconciliation results for a specific run.
   - Response:
     - `200 OK`
     - JSON array of reconciliation results.
     - `404 Not Found` if run does not exist.

5. Get Breaks and Missing Trades
   - Endpoint: `GET /reconciliation/runs/<run_id>/breaks`
   - Description: Returns only the BREAK and MISSING records for a run.
   - Optionally filter by a specific field (e.g., price).
   - Query Parameters:
     - `field` (optional): Filter breaks by a specific field (e.g., `price`).
   - Response:
     - `200 OK`
     - JSON array of breaks and missing trades.
     - `404 Not Found` if run does not exist.

### Example Requests

```bash
# Trigger a new run
POST http://localhost:5000/reconciliation/run

# List all past runs
GET http://localhost:5000/reconciliation/runs

# Get summary for Run ID 1
GET http://localhost:5000/reconciliation/runs/1/summary

# Get breaks and missing for Run ID 1
GET http://localhost:5000/reconciliation/runs/1/breaks

# Filter breaks by price for Run ID 1
GET http://localhost:5000/reconciliation/runs/1/breaks?field=price
```

### Importing the Collection into Postman

1. Open Postman.
2. Click the Import button (top left).
3. Select the File tab.
4. Click Choose Files and select `TradeRecon.postman_collection.json` from your project directory.
5. Click Import.
6. The collection will appear in your Postman sidebar, ready to use.
