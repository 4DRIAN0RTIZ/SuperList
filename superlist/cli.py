import json
from datetime import datetime

import click
from flask import current_app

from .config import BASE_DIR
from .extensions import db
from .models import Purchase, PurchaseItem

_LEGACY_TS_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")


def _parse_timestamp(raw: str) -> datetime:
    for fmt in _LEGACY_TS_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.fromisoformat(raw)


def register_cli(app):
    app.cli.add_command(init_db)
    app.cli.add_command(import_history)


@click.command("init-db")
def init_db():
    """Create tables from the models. Use only for a brand-new database
    without migration history; otherwise run `flask db upgrade`."""
    db.create_all()
    click.echo("Tables created.")


@click.command("import-history")
@click.option(
    "--path",
    "path",
    default=None,
    help="Path to the legacy history.json (defaults to the project root).",
)
def import_history(path):
    """Import purchases from the pre-SQLite history.json. Idempotent:
    a purchase already present (same name and timestamp) is skipped."""
    source = path or (BASE_DIR / "history.json")
    with open(source, encoding="utf-8") as fh:
        payload = json.load(fh)

    imported = skipped = 0
    for entry in payload:
        name = entry["name"].strip()
        timestamp = _parse_timestamp(entry["timestamp"])

        exists = Purchase.query.filter_by(name=name, timestamp=timestamp).first()
        if exists is not None:
            skipped += 1
            continue

        purchase = Purchase(
            name=name,
            total=float(entry.get("total", 0.0)),
            budget=float(entry.get("budget", 0.0)),
            timestamp=timestamp,
        )
        for item in entry.get("items", []):
            purchase.items.append(
                PurchaseItem(
                    name=item["name"].strip(),
                    price=float(item.get("price", 0.0)),
                    quantity=int(item.get("cantidad", item.get("quantity", 1))),
                )
            )
        db.session.add(purchase)
        imported += 1

    db.session.commit()
    click.echo(f"Imported {imported} purchase(s), skipped {skipped} already present.")
    current_app.logger.info("history.json import: +%d, skipped %d", imported, skipped)
