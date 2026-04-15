from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Run(db.Model):
    __tablename__ = "runs"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    total_internal = db.Column(db.Integer, default=0)
    total_external = db.Column(db.Integer, default=0)
    matched_count = db.Column(db.Integer, default=0)
    break_count = db.Column(db.Integer, default=0)
    missing_internal_count = db.Column(db.Integer, default=0)
    missing_external_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "run_id": self.id,
            "created_at": self.created_at.isoformat(),
            "total_internal": self.total_internal,
            "total_external": self.total_external,
            "matched_count": self.matched_count,
            "break_count": self.break_count,
            "missing_internal_count": self.missing_internal_count,
            "missing_external_count": self.missing_external_count,
        }


class Trade(db.Model):
    __tablename__ = "trades"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=False)
    source = db.Column(db.String(50), nullable=False)  # 'internal' or 'external'

    # Trade fields
    trade_id = db.Column(db.String(50), nullable=False)
    instrument = db.Column(db.String(50))
    trade_date = db.Column(db.String(20))
    settlement_date = db.Column(db.String(20))
    direction = db.Column(db.String(10))
    quantity = db.Column(db.Float)
    price = db.Column(db.Float)
    currency = db.Column(db.String(10))
    counterparty = db.Column(db.String(50))
    status = db.Column(db.String(20))


class ReconResult(db.Model):
    __tablename__ = "recon_results"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=False)
    trade_id = db.Column(db.String(50), nullable=False)
    status = db.Column(
        db.String(50), nullable=False
    )  # MATCHED, BREAK, MISSING_INTERNAL, MISSING_EXTERNAL

    def to_dict(self):
        return {"trade_id": self.trade_id, "status": self.status}


class BreakDetail(db.Model):
    __tablename__ = "break_details"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=False)
    trade_id = db.Column(db.String(50), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)  # e.g., 'price', 'quantity'
    internal_value = db.Column(db.String(255))
    external_value = db.Column(db.String(255))

    def to_dict(self):
        return {
            "trade_id": self.trade_id,
            "field_name": self.field_name,
            "internal_value": self.internal_value,
            "external_value": self.external_value,
        }
