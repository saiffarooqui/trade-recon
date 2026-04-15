import pandas as pd
import logging
import os
from app.models import db, Trade

# Configure basic logging to the console
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

VALID_DIRECTIONS = {"BUY", "SELL"}
VALID_STATUSES = {"SETTLED", "PENDING", "CANCELLED"}


def validate_row(row):
    """Validates a single CSV row based on business rules."""
    required_fields = [
        "trade_id",
        "instrument",
        "direction",
        "quantity",
        "price",
        "status",
    ]

    # 1. Check missing required fields
    for field in required_fields:
        if pd.isna(row.get(field)) or str(row.get(field)).strip() == "":
            raise ValueError(f"Missing required field: '{field}'")

    # 2. Validate enum values
    if str(row["direction"]).strip().upper() not in VALID_DIRECTIONS:
        raise ValueError(f"Invalid direction: {row['direction']}")

    if str(row["status"]).strip().upper() not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {row['status']}")

    # 3. Validate numeric types
    try:
        float(row["quantity"])
        float(row["price"])
    except ValueError:
        raise ValueError("Quantity and Price must be valid numbers")


def ingest_csv(file_path, source_name, run_id):
    """
    Reads a CSV, validates rows, and saves valid trades to the database.
    Returns the count of successfully ingested records.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return 0

    try:
        # Read CSV, treating empty strings as NaNs for easier validation
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        logger.error(f"Failed to read CSV {file_path}: {e}")
        return 0

    successful_inserts = 0

    for index, row in df.iterrows():
        try:
            # Run our validation rules
            validate_row(row)

            # Map to database model
            trade = Trade(
                run_id=run_id,
                source=source_name,
                trade_id=str(row["trade_id"]).strip(),
                instrument=str(row.get("instrument", "")).strip(),
                trade_date=str(row.get("trade_date", "")).strip(),
                settlement_date=str(row.get("settlement_date", "")).strip(),
                direction=str(row["direction"]).strip().upper(),
                quantity=float(row["quantity"]),
                price=float(row["price"]),
                currency=str(row.get("currency", "")).strip().upper(),
                counterparty=str(row.get("counterparty", "")).strip(),
                status=str(row["status"]).strip().upper(),
            )

            db.session.add(trade)
            successful_inserts += 1

        except ValueError as e:
            # If malformed, log and continue
            logger.warning(f"Row {index + 2} in {source_name} skipped. Reason: {e}")
            continue

    # Commit all successful inserts for this file at once
    db.session.commit()
    logger.info(f"Successfully ingested {successful_inserts} trades from {source_name}")

    return successful_inserts
