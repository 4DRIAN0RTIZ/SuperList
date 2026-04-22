from .extensions import db
from datetime import datetime

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    checked = db.Column(db.Boolean, default=False, nullable=False)
    price = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "checked": self.checked,
            "price": self.price,
            "quantity": self.quantity,
        }

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, default=0.0, nullable=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    total = db.Column(db.Float, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("PurchaseItem", backref="purchase", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "total": self.total,
            "budget": self.budget,
            "timestamp": self.timestamp.isoformat(),
            "items": [item.to_dict() for item in self.items]
        }

class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchase.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
        }
