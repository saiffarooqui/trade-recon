import os
from flask import Blueprint, jsonify, request
from pathlib import Path
from app.models import db, Run, ReconResult, BreakDetail
from app.services.ingestor import ingest_csv
from app.services.reconciler import reconcile_run

# Create a Blueprint prefixed with /reconciliation
recon_bp = Blueprint("recon", __name__, url_prefix="/reconciliation")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERNAL_FILE_PATH = PROJECT_ROOT / "data/internal_trades.csv"
EXTERNAL_FILE_PATH = PROJECT_ROOT / "data/external_trades.csv"


@recon_bp.route("/run", methods=["POST"])
def run_reconciliation():
    """Trigger a new reconciliation run."""
    # 1. Create a new Run record
    new_run = Run()
    db.session.add(new_run)
    db.session.commit()  # Commit to get the run.id

    # 2. Ingest the data
    ingest_csv(INTERNAL_FILE_PATH, "internal", new_run.id)
    ingest_csv(EXTERNAL_FILE_PATH, "external", new_run.id)

    # 3. Run the reconciliation engine
    summary = reconcile_run(new_run.id)

    if not summary:
        return jsonify({"error": "Reconciliation failed"}), 500

    return jsonify({"message": "Reconciliation complete", "data": summary}), 201


@recon_bp.route("/runs", methods=["GET"])
def get_runs():
    """List all past runs with summary counts."""
    runs = Run.query.order_by(Run.created_at.desc()).all()
    return jsonify({"data": [run.to_dict() for run in runs]}), 200


@recon_bp.route("/runs/<int:run_id>/summary", methods=["GET"])
def get_run_summary(run_id):
    """Matched / breaks / missing counts for a specific run."""
    run = Run.query.get(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404

    return jsonify({"data": run.to_dict()}), 200


@recon_bp.route("/runs/<int:run_id>", methods=["GET"])
def get_full_results(run_id):
    """Full results for a specific run."""
    run = Run.query.get(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404

    results = ReconResult.query.filter_by(run_id=run_id).all()
    return jsonify({"data": [res.to_dict() for res in results]}), 200


@recon_bp.route("/runs/<int:run_id>/breaks", methods=["GET"])
def get_breaks(run_id):
    """
    Only the BREAK and MISSING records.
    Also handles filtering breaks by field: ?field=price.
    """
    run = Run.query.get(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404

    field_filter = request.args.get("field")

    if field_filter:
        # If filtering by a specific field (e.g., ?field=price)
        breaks = BreakDetail.query.filter_by(
            run_id=run_id, field_name=field_filter
        ).all()
        return jsonify({"data": [b.to_dict() for b in breaks]}), 200
    else:
        # General breaks and missing records
        results = ReconResult.query.filter(
            ReconResult.run_id == run_id,
            ReconResult.status.in_(["BREAK", "MISSING_INTERNAL", "MISSING_EXTERNAL"]),
        ).all()

        # To make the UI easier to build later, let's attach the break details to the response
        break_details = BreakDetail.query.filter_by(run_id=run_id).all()
        details_map = {}
        for detail in break_details:
            if detail.trade_id not in details_map:
                details_map[detail.trade_id] = []
            details_map[detail.trade_id].append(detail.to_dict())

        response_data = []
        for res in results:
            item = res.to_dict()
            if res.status == "BREAK":
                item["details"] = details_map.get(res.trade_id, [])
            response_data.append(item)

        return jsonify({"data": response_data}), 200
