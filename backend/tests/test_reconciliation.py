import pytest
from app.services.reconciler import reconcile_run
from app.models import db, Trade, Run, ReconResult, BreakDetail


def test_reconciliation_logic(app):
    with app.app_context():
        # 1. Setup a mock Run
        run = Run()
        db.session.add(run)
        db.session.commit()

        # 2. Seed a Known Small Dataset directly into the DB

        # Trade 1: MATCHED
        t1_int = Trade(
            run_id=run.id,
            source="internal",
            trade_id="1",
            direction="BUY",
            quantity=100,
            price=150.0,
            status="SETTLED",
            settlement_date="2026-04-12",
            currency="USD",
        )
        t1_ext = Trade(
            run_id=run.id,
            source="external",
            trade_id="1",
            direction="BUY",
            quantity=100,
            price=150.0,
            status="SETTLED",
            settlement_date="2026-04-12",
            currency="USD",
        )

        # Trade 2: BREAK (Price Mismatch)
        t2_int = Trade(
            run_id=run.id,
            source="internal",
            trade_id="2",
            direction="SELL",
            quantity=200,
            price=310.5,
            status="SETTLED",
            settlement_date="2026-04-12",
            currency="USD",
        )
        t2_ext = Trade(
            run_id=run.id,
            source="external",
            trade_id="2",
            direction="SELL",
            quantity=200,
            price=310.0,
            status="SETTLED",
            settlement_date="2026-04-12",
            currency="USD",
        )

        # Trade 3: MISSING_EXTERNAL (Exists in Internal, missing in External)
        t3_int = Trade(
            run_id=run.id,
            source="internal",
            trade_id="3",
            direction="BUY",
            quantity=50,
            price=200.0,
            status="PENDING",
            settlement_date="2026-04-12",
            currency="USD",
        )

        # Trade 4: MISSING_INTERNAL (Exists in External, missing in Internal)
        t4_ext = Trade(
            run_id=run.id,
            source="external",
            trade_id="4",
            direction="SELL",
            quantity=150,
            price=130.0,
            status="SETTLED",
            settlement_date="2026-04-13",
            currency="USD",
        )

        db.session.add_all([t1_int, t1_ext, t2_int, t2_ext, t3_int, t4_ext])
        db.session.commit()

        # 3. Execute the engine
        summary = reconcile_run(run.id)

        # 4. Verify exact counts
        assert summary["matched_count"] == 1
        assert summary["break_count"] == 1
        assert summary["missing_external_count"] == 1
        assert summary["missing_internal_count"] == 1

        # 5. Verify the Price Break detail was recorded accurately
        breaks = BreakDetail.query.all()
        assert len(breaks) == 1
        assert breaks[0].trade_id == "2"
        assert breaks[0].field_name == "price"
        assert breaks[0].internal_value == "310.5"
        assert breaks[0].external_value == "310.0"

        # 6. Verify final statuses in ReconResult table
        results = ReconResult.query.all()
        status_map = {r.trade_id: r.status for r in results}
        assert status_map["1"] == "MATCHED"
        assert status_map["2"] == "BREAK"
        assert status_map["3"] == "MISSING_EXTERNAL"
        assert status_map["4"] == "MISSING_INTERNAL"
