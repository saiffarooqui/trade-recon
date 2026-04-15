import logging
from app.models import db, Trade, ReconResult, BreakDetail, Run

logger = logging.getLogger(__name__)

# The specific fields the requirements asked us to compare
FIELDS_TO_COMPARE = [
    "quantity",
    "price",
    "settlement_date",
    "direction",
    "status",
    "currency",
]


def reconcile_run(run_id):
    """
    Executes the reconciliation logic for a specific run_id.
    Compares internal vs external trades, saves the results, and updates the run summary.
    """
    logger.info(f"Starting reconciliation for run_id: {run_id}")

    # 1. Fetch the run record to update later
    run = Run.query.get(run_id)
    if not run:
        logger.error(f"Run {run_id} not found.")
        return None

    # 2. Fetch all trades for this run from the database
    all_trades = Trade.query.filter_by(run_id=run_id).all()

    # Organize trades by source and trade_id for O(1) lookups
    internal_trades = {t.trade_id: t for t in all_trades if t.source == "internal"}
    external_trades = {t.trade_id: t for t in all_trades if t.source == "external"}

    run.total_internal = len(internal_trades)
    run.total_external = len(external_trades)

    # Combine all unique trade IDs from both systems
    all_trade_ids = set(internal_trades.keys()).union(set(external_trades.keys()))

    matched_count = 0
    break_count = 0
    missing_internal_count = 0
    missing_external_count = 0

    # 3. Iterate through every unique trade ID and compare
    for trade_id in all_trade_ids:
        internal = internal_trades.get(trade_id)
        external = external_trades.get(trade_id)

        status = None

        if internal and not external:
            # Exists only in internal
            status = "MISSING_EXTERNAL"
            missing_internal_count += 1

        elif external and not internal:
            # Exists only in external
            status = "MISSING_INTERNAL"
            missing_external_count += 1

        else:
            # Trade exists in both, we must compare the fields
            is_break = False

            for field in FIELDS_TO_COMPARE:
                int_val = getattr(internal, field)
                ext_val = getattr(external, field)

                # Check for mismatch
                if int_val != ext_val:
                    is_break = True
                    # Record the exact field that broke
                    break_detail = BreakDetail(
                        run_id=run_id,
                        trade_id=trade_id,
                        field_name=field,
                        internal_value=str(int_val),
                        external_value=str(ext_val),
                    )
                    db.session.add(break_detail)

            if is_break:
                status = "BREAK"
                break_count += 1
            else:
                status = "MATCHED"
                matched_count += 1

        # Save the high-level result for this trade
        recon_result = ReconResult(run_id=run_id, trade_id=trade_id, status=status)
        db.session.add(recon_result)

    # 4. Update the Run summary counts
    run.matched_count = matched_count
    run.break_count = break_count
    run.missing_internal_count = missing_internal_count
    run.missing_external_count = missing_external_count

    # Commit all changes to the database
    db.session.commit()

    logger.info(
        f"Run {run_id} complete: {matched_count} Matched, {break_count} Breaks, "
        f"{missing_internal_count} Missing Internal, {missing_external_count} Missing External"
    )

    return run.to_dict()
