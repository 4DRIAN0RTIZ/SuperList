from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "shopping_list.json"
BUDGET_FILE = "budget.json"
HISTORY_FILE = "history.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_budget():
    if not os.path.exists(BUDGET_FILE):
        return 0.0
    with open(BUDGET_FILE, "r") as f:
        try:
            return float(json.load(f))
        except:
            return 0.0

def save_budget(budget):
    with open(BUDGET_FILE, "w") as f:
        json.dump(budget, f)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

@app.route("/")
def index():
    items = load_data()
    total = sum((item.get("price", 0) or 0) * (item.get("cantidad", 1) or 1) for item in items if item.get("checked"))
    budget = load_budget()
    history = load_history()
    last_purchase = None
    if history:
        last_purchase = history[-1]
        last_purchase["timestamp"] = datetime.strptime(last_purchase["timestamp"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
    diff = budget - total
    return render_template("index.html", items=items, total=total, budget=budget, diff=diff, latest_purchase=last_purchase)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("index"))
    items = load_data()
    items.append({"name": name, "checked": False, "price": 0, "cantidad": 1})
    save_data(items)
    return redirect(url_for("index"))

@app.route("/check/<int:item_id>", methods=["POST"])
def check(item_id):
    items = load_data()
    if 0 <= item_id < len(items):
        items[item_id]["checked"] = not items[item_id].get("checked", False)
        if not items[item_id]["checked"]:
            items[item_id]["price"] = 0
            items[item_id]["cantidad"] = 1
        save_data(items)
    return redirect(url_for("index"))

@app.route("/set_price/<int:item_id>", methods=["POST"])
def set_price(item_id):
    price = request.form.get("price", "0").strip()
    cantidad = request.form.get("cantidad", "1").strip()
    try:
        price_val = float(price)
        if price_val < 0:
            price_val = 0.0
    except:
        price_val = 0.0

    try:
        cantidad_val = int(cantidad)
        if cantidad_val < 1:
            cantidad_val = 1
    except:
        cantidad_val = 1

    items = load_data()
    if 0 <= item_id < len(items):
        items[item_id]["price"] = price_val
        items[item_id]["cantidad"] = cantidad_val
        save_data(items)
    return redirect(url_for("index"))

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    items = load_data()
    if 0 <= item_id < len(items):
        items.pop(item_id)
        save_data(items)
    return redirect(url_for("index"))

@app.route("/reset", methods=["POST"])
def reset():
    save_data([])
    return redirect(url_for("index"))

@app.route("/set_budget", methods=["POST"])
def set_budget():
    budget = request.form.get("budget", "0").strip()
    try:
        budget_val = float(budget)
        if budget_val < 0:
            budget_val = 0.0
    except:
        budget_val = 0.0
    save_budget(budget_val)
    return redirect(url_for("index"))

@app.route("/save_purchase", methods=["POST"])
def save_purchase():
    name = request.form.get("purchase_name", "").strip()
    if not name:
        name = f"Compra sin nombre - {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    items = load_data()
    total = sum((item.get("price", 0) or 0) * (item.get("cantidad", 1) or 1) for item in items if item.get("checked"))
    budget = load_budget()

    history = load_history()
    history.append({
        "name": name,
        "items": items,
        "total": total,
        "budget": budget,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_history(history)
    save_data([])  # limpia actual
    return redirect(url_for("history"))

@app.route("/history")
def history():
    records = load_history()
    return render_template("history.html", compras=records)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
