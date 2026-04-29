import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE ----------------
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ---------------- INIT TABLE ----------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            title TEXT,
            category TEXT,
            amount NUMERIC
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()

# ---------------- ROOT ----------------
@app.route("/")
def home():
    return "OK"

# ---------------- ADD EXPENSE ----------------
@app.route("/add-expense", methods=["POST"])
def add_expense():
    data = request.get_json()

    title = data.get("title")
    category = data.get("category")
    amount = data.get("amount")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO expenses (title, category, amount) VALUES (%s, %s, %s) RETURNING id",
        (title, category, amount)
    )

    new_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": new_id,
        "message": "Expense added"
    })

# ---------------- GET ALL EXPENSES ----------------
@app.route("/expenses", methods=["GET"])
def get_expenses():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, title, category, amount FROM expenses ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "title": r[1],
            "category": r[2],
            "amount": float(r[3])
        })

    return jsonify(result)

# ---------------- SUMMARY ----------------
@app.route("/summary", methods=["GET"])
def summary():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM expenses")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({
        "total_expense": float(total),
        "total_entries": count
    })

# ---------------- DELETE ----------------
@app.route("/delete-expense/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Deleted successfully"})