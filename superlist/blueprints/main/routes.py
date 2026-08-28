from flask import render_template, request, url_for, jsonify
from datetime import datetime

from ...extensions import db
from ...models import Item, Budget, Purchase, PurchaseItem
from . import bp


@bp.route("/")
def index():
    return render_template("index.html", active_page='index')


@bp.route("/data")
def get_data():
    items = Item.query.order_by(Item.id).all()
    total = sum(item.price * item.quantity for item in items if item.checked)
    budget = Budget.current()
    latest_purchase = Purchase.query.order_by(Purchase.timestamp.desc()).first()

    diff = budget.value - total

    return jsonify({
        "items": [item.to_dict() for item in items],
        "total": total,
        "budget": budget.value,
        "diff": diff,
        "latest_purchase": latest_purchase.to_dict() if latest_purchase else None
    })


@bp.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    name = data.get("name", "").strip()
    if name:
        new_item = Item(name=name)
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict())
    return jsonify({"error": "Name is required"}), 400


@bp.route("/check/<int:item_id>", methods=["POST"])
def check(item_id):
    item = Item.query.get_or_404(item_id)
    item.checked = not item.checked
    if not item.checked:
        item.price = 0.0
        item.quantity = 1
    db.session.commit()
    return jsonify(item.to_dict())


@bp.route("/set_price/<int:item_id>", methods=["POST"])
def set_price(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    try:
        price = float(data.get("price", "0").strip())
        quantity = int(data.get("quantity", "1").strip())
        item.price = max(0.0, price)
        item.quantity = max(1, quantity)
        db.session.commit()
        return jsonify(item.to_dict())
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price or quantity"}), 400


@bp.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": True})


@bp.route("/reset", methods=["POST"])
def reset():
    Item.query.delete()
    db.session.commit()
    return jsonify({"success": True})


@bp.route("/set_budget", methods=["POST"])
def set_budget():
    budget = Budget.current()
    data = request.get_json()
    try:
        new_value = float(data.get("budget", "0").strip())
        budget.value = max(0.0, new_value)
        db.session.commit()
        return jsonify({"budget": budget.value})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid budget value"}), 400


@bp.route("/save_purchase", methods=["POST"])
def save_purchase():
    data = request.get_json()
    name = data.get("purchase_name", "").strip()
    if not name:
        name = f"Purchase on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    items = Item.query.filter_by(checked=True).all()
    if not items:
        return jsonify({"error": "No items selected to save."}), 400

    total = sum(item.price * item.quantity for item in items)
    budget = Budget.current().value

    new_purchase = Purchase(name=name, total=total, budget=budget)
    for item in items:
        p_item = PurchaseItem(name=item.name, price=item.price, quantity=item.quantity, purchase=new_purchase)
        db.session.add(p_item)
        db.session.delete(item)

    db.session.add(new_purchase)
    db.session.commit()
    return jsonify({"success": True, "redirect_url": url_for("main.history")})


@bp.route("/comparador")
def comparador():
    return render_template("comparador.html", active_page='comparador', page_title='Comparador — SuperLista')


@bp.route("/history")
def history():
    purchases = Purchase.query.order_by(Purchase.timestamp.desc()).all()
    return render_template(
        "history.html",
        compras=purchases,
        active_page='history',
        page_title='Historial — SuperLista'
    )
