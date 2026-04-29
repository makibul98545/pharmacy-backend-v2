import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# --- INIT TABLE ---
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            title TEXT,
            category TEXT,
            amount FLOAT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- ROUTES ---
@app.route("/")
def home():
    return "OK"

@app.route("/add-expense", methods=["POST"])
def add_expense():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO expenses (title, category, amount) VALUES (%s, %s, %s) RETURNING id;",
        (data["title"], data["category"], data["amount"])
    )

    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Expense added", "id": new_id})

@app.route("/expenses", methods=["GET"])
def get_expenses():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, title, category, amount FROM expenses ORDER BY id DESC;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = [
        {"id": r[0], "title": r[1], "category": r[2], "amount": r[3]}
        for r in rows
    ]

    return jsonify(data)

@app.route("/summary", methods=["GET"])
def get_summary():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses")
    total_expense = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM expenses")
    total_entries = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({
        "total_expense": float(total_expense),
        "total_entries": total_entries
    })

@app.route("/expenses", methods=["GET"])
def get_expenses():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, title, category, amount FROM expenses ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "title": row[1],
            "category": row[2],
            "amount": float(row[3])
        })

    return jsonify(data)   

@app.route("/delete-expense/<int:id>", methods=["DELETE"])
def delete_expense(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id=%s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Deleted successfully"})