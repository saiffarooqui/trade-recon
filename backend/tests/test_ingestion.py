import os
import pytest
from app.services.ingestor import ingest_csv
from app.models import Trade, db


def test_ingestion_success_and_error_handling(app, tmp_path):
    # create a temporary CSV file with 2 valid rows and 2 malformed rows
    csv_content = """trade_id,instrument,trade_date,settlement_date,direction,quantity,price,currency,counterparty,status
1,AAPL,2026-04-10,2026-04-12,BUY,100,150.00,USD,JPM,SETTLED
2,MSFT,2026-04-10,2026-04-12,INVALID_DIR,200,310.50,USD,GS,SETTLED
3,TSLA,2026-04-10,2026-04-12,BUY,invalid_qty,200.00,USD,MS,PENDING
4,GOOGL,2026-04-11,2026-04-13,SELL,150,130.00,USD,CITI,SETTLED"""

    # tmp_path is a built-in pytest fixture that provides a temporary directory
    file_path = tmp_path / "test_trades.csv"
    file_path.write_text(csv_content)

    with app.app_context():
        # Trigger ingestion
        success_count = ingest_csv(str(file_path), "internal", 1)

        # Assert only the 2 valid rows were ingested
        assert success_count == 2
        trades = Trade.query.order_by(Trade.trade_id).all()
        assert len(trades) == 2

        # Verify the valid trade IDs made it into the DB
        assert trades[0].trade_id == "1"
        assert trades[1].trade_id == "4"
