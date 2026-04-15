import React from "react";

export default function BreaksTable({ breaks }) {
  if (!breaks || breaks.length === 0)
    return <p>No breaks found for this run.</p>;

  // Flatten the details array for BREAKs so we can render a row per broken field
  const rows = [];
  breaks.forEach((record) => {
    if (record.status === "BREAK" && record.details) {
      record.details.forEach((detail) => {
        rows.push({
          trade_id: record.trade_id,
          status: record.status,
          field: detail.field_name,
          internal: detail.internal_value,
          external: detail.external_value,
        });
      });
    } else {
      // For MISSING_INTERNAL or MISSING_EXTERNAL
      rows.push({
        trade_id: record.trade_id,
        status: record.status,
        field: "N/A",
        internal: record.status === "MISSING_EXTERNAL" ? "Exists" : "Missing",
        external: record.status === "MISSING_INTERNAL" ? "Exists" : "Missing",
      });
    }
  });

  return (
    <div>
      <h2>Discrepancies Report</h2>
      <table>
        <thead>
          <tr>
            <th>Trade ID</th>
            <th>Status</th>
            <th>Field</th>
            <th>Internal Value</th>
            <th>External Value</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={`${row.trade_id}-${idx}`}>
              <td>
                <strong>{row.trade_id}</strong>
              </td>
              <td>
                <span
                  className={`status-badge ${row.status === "BREAK" ? "bg-red" : "bg-orange"}`}
                >
                  {row.status}
                </span>
              </td>
              <td>{row.field}</td>
              <td>{row.internal}</td>
              <td>{row.external}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
