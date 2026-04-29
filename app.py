from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory store (temporary; will switch to PostgreSQL next)
expenses = []

@app.route("/")
def home():
    return "OK"

@app.route("/add-expense", methods=["POST"])
def add_expense():
    data = request.get_json()

    title = data.get("title")
    category = data.get("category")
    amount = float(data.get("amount", 0))

    expense = {
        "id": len(expenses) + 1,
        "title": title,
        "category": category,
        "amount": amount
    }

    expenses.append(expense)

    return jsonify({"message": "Expense added", "data": expense})


@app.route("/expenses", methods=["GET"])
def get_expenses():
    return jsonify(expenses)


@app.route("/summary", methods=["GET"])
def summary():
    total_purchase = sum(e["amount"] for e in expenses)
    total_payment = 0  # extend later if needed
    net = total_purchase - total_payment
    closing_balance = net

    return jsonify({
        "total_purchase": total_purchase,
        "total_payment": total_payment,
        "net": net,
        "closing_balance": closing_balance
    })


if __name__ == "__main__":
    app.run(debug=True)