# SuperList

SuperList is a small web app for planning your grocery shopping. Add the products you need with their price and quantity, set a budget, and see the total as you go.

## What you can do

- Build a shopping list with price and quantity for each product.
- Set a budget and keep an eye on how much you have left.
- Review your past purchases in the history page.
- Compare products by price per unit to find the better deal.

## Getting started

You need Python 3.10 or newer.

```bash
git clone https://github.com/4DRIAN0RTIZ/SuperList.git
cd SuperList

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
flask --app run db upgrade
python run.py
```

Then open http://localhost:5002 in your browser.

## Configuration

Settings live in the `.env` file (copied from `.env.example`):

| Variable       | What it does                                                          |
|----------------|-----------------------------------------------------------------------|
| `FLASK_ENV`    | `development`, `testing` or `production`.                             |
| `SECRET_KEY`   | Required in production. Use a long random value and keep it private.  |
| `DATABASE_URL` | Optional. By default the data is stored in `instance/superlist.db`.   |
| `PORT`         | Port for the development server (default `5002`).                     |

## Built with

Flask, SQLAlchemy and SQLite.

## Releases

The changelog is generated automatically from commit messages. See [CHANGELOG.md](CHANGELOG.md).
