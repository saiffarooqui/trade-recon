import pytest
from app.models import db, Run, ReconResult, BreakDetail


def test_get_runs(client, app):
    """Test retrieving a list of all runs."""
    with app.app_context():
        run = Run(matched_count=10, break_count=5)
        db.session.add(run)
        db.session.commit()

    response = client.get("/reconciliation/runs")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data) == 1
    assert data[0]["matched_count"] == 10


def test_get_breaks_with_filter(client, app):
    """Test retrieving breaks and applying the ?field= filter."""
    with app.app_context():
        run = Run()
        db.session.add(run)
        db.session.commit()

        rr = ReconResult(run_id=run.id, trade_id="99", status="BREAK")
        bd = BreakDetail(
            run_id=run.id,
            trade_id="99",
            field_name="price",
            internal_value="100.0",
            external_value="101.0",
        )
        db.session.add_all([rr, bd])
        db.session.commit()

        run_id = run.id

    # 1. Get all breaks
    response = client.get(f"/reconciliation/runs/{run_id}/breaks")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data) == 1
    assert data[0]["trade_id"] == "99"
    assert data[0]["details"][0]["field_name"] == "price"

    # 2. Filter by price (should return the break detail)
    response_price = client.get(f"/reconciliation/runs/{run_id}/breaks?field=price")
    assert response_price.status_code == 200
    assert len(response_price.get_json()["data"]) == 1

    # 3. Filter by quantity (should return empty, since this break was a price break)
    response_qty = client.get(f"/reconciliation/runs/{run_id}/breaks?field=quantity")
    assert response_qty.status_code == 200
    assert len(response_qty.get_json()["data"]) == 0
