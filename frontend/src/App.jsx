import { useState, useEffect } from "react";
import axios from "axios";
import BreaksTable from "./components/BreaksTable";
import "./App.css";

const API_BASE = "http://localhost:5000/reconciliation";

function App() {
  const [runs, setRuns] = useState([]);
  const [activeRun, setActiveRun] = useState(null);
  const [activeBreaks, setActiveBreaks] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch all runs on component mount
  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      const res = await axios.get(`${API_BASE}/runs`);
      setRuns(res.data.data);
      if (res.data.data.length > 0 && !activeRun) {
        // Auto-select the most recent run
        selectRun(res.data.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch runs", err);
    }
  };

  const selectRun = async (run) => {
    setActiveRun(run);
    try {
      const res = await axios.get(`${API_BASE}/runs/${run.run_id}/breaks`);
      setActiveBreaks(res.data.data);
    } catch (err) {
      console.error("Failed to fetch breaks", err);
    }
  };

  const triggerRun = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/run`);
      const newRun = res.data.data;
      await fetchRuns(); // Refresh list
      selectRun(newRun); // Select the newly created run
    } catch (err) {
      alert("Error triggering run. Is the Flask backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Trade Recon Dashboard</h1>
        <button onClick={triggerRun} disabled={loading}>
          {loading ? "Running..." : "▶ Trigger New Run"}
        </button>
      </header>

      {/* Select a historical run if multiple exist */}
      {runs.length > 0 && (
        <div style={{ marginBottom: "20px" }}>
          <label style={{ fontWeight: "bold", marginRight: "10px" }}>
            View Run:
          </label>
          <select
            value={activeRun?.run_id || ""}
            onChange={(e) =>
              selectRun(runs.find((r) => r.run_id === parseInt(e.target.value)))
            }
          >
            {runs.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                Run #{r.run_id} - {new Date(r.created_at).toLocaleString()}
              </option>
            ))}
          </select>
        </div>
      )}

      {activeRun && (
        <>
          <div className="summary-cards">
            <div className="card">
              <h3>Total Trades (Int / Ext)</h3>
              <p>
                {activeRun.total_internal} / {activeRun.total_external}
              </p>
            </div>
            <div className="card match">
              <h3>Matched</h3>
              <p>{activeRun.matched_count}</p>
            </div>
            <div className="card break">
              <h3>Breaks</h3>
              <p>{activeRun.break_count}</p>
            </div>
            <div className="card">
              <h3>Missing (Int / Ext)</h3>
              <p>
                {activeRun.missing_internal_count} /{" "}
                {activeRun.missing_external_count}
              </p>
            </div>
          </div>

          <BreaksTable breaks={activeBreaks} />
        </>
      )}

      {!activeRun && !loading && (
        <p>No runs found. Click "Trigger New Run" to start.</p>
      )}
    </div>
  );
}

export default App;
