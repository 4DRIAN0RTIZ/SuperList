from datetime import datetime, timezone

from .extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    checked = db.Column(db.Boolean, default=False, nullable=False, index=True)
    price = db.Column(db.Float, default=0.0, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "checked": self.checked,
            "price": self.price,
            "quantity": self.quantity,
        }


class Budget(db.Model):
    __tablename__ = "budget"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, default=0.0, nullable=False)

    @classmethod
    def current(cls):
        """Return the single budget row, creating it on first access."""
        budget = cls.query.first()
        if budget is None:
            budget = cls(value=0.0)
            db.session.add(budget)
            db.session.commit()
        return budget


class Purchase(db.Model):
    __tablename__ = "purchase"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    total = db.Column(db.Float, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=_utcnow, nullable=False, index=True)
    items = db.relationship(
        "PurchaseItem",
        back_populates="purchase",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "total": self.total,
            "budget": self.budget,
            "timestamp": self.timestamp.isoformat(),
            "items": [item.to_dict() for item in self.items],
        }


class PurchaseItem(db.Model):
    __tablename__ = "purchase_item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchase.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purchase = db.relationship("Purchase", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
        }
