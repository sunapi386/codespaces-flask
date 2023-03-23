import json
import uuid
from flask import Flask, jsonify, make_response, render_template, request
import sqlite3


app = Flask(__name__)


class Entry:
    def __init__(self, id, direction, amount):
        if direction not in ["debit", "credit"]:
            raise ValueError("Invalid direction")

        self.id :str = id
        self.direction :str = direction
        self.amount :int = amount

    def __repr__(self):
        return json.dumps(self.__dict__)


@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.get("/account/<id>")
def get_account(id: str):
    con = sqlite3.connect("app.db")
    cur = con.cursor()
    # make sure id exists
    res = cur.execute("SELECT * FROM account WHERE id = ?", (id,))
    tables = res.fetchone()

    return jsonify(tables)

@app.post("/account")
def create_account():
    con = sqlite3.connect("app.db")
    # validate the json; balance and direction must exist
    j = request.json
    if not j or "direction" not in j or j["direction"] not in ["debit", "credit"]:
        return make_response(jsonify({"error": "Invalid request"}), 400)


    # if id is provided, check if the account already exists
    if "id" in j:
        cur = con.cursor()
        res = cur.execute("SELECT 1 FROM account WHERE id = ?", (j["id"],))
        tables = res.fetchone()
        if tables:
            return make_response(jsonify({"error": "Account already exists"}), 400)

    # create the account
    cur = con.cursor()
    name = j["name"] if "name" in j else "New Account"
    new_id = str(uuid.uuid4())
    cur.execute("INSERT INTO account (id, name, balance, direction) VALUES (?, ?, ?, ?)",
                      new_id, name, 0, j["direction"])
    # return the response
    return get_account(new_id)

# transactions
@app.get("/transactions/<id>")
def get_transaction(id: str):
    con = sqlite3.connect("app.db")
    cur = con.cursor()
    # make sure id exists
    res = cur.execute("SELECT * FROM transactions WHERE id = ?", (id,))
    tables = res.fetchone()
    return jsonify(tables)


def validate_transaction_entries(entries: list):
    sum = 0
    # assuming entries are valid -- todo: enforce in code
    for e in entries:
        if e["direction"] == "debit":
            sum -= e["amount"]
        elif e["direction"] == "credit":
            sum += e["amount"]

    return sum == 0

def apply_entries_to_account(entries: list):

    for e in entries:
        # check if account exists
        if e["direction"] == "debit":
            # debit the account
            pass
        elif e["direction"] == "credit":
            # credit the account
            pass

@app.post("/transactions")
def post_transaction():
    j = request.json
    if not validate_transaction_entries(j['entries']):
        return "Invalid transaction", 400
    apply_entries_to_account(j['entries'])

    # con = sqlite3.connect("app.db")
    # cur = con.cursor()
    # # make sure id exists
    # res = cur.execute("SELECT * FROM transactions WHERE id = ?", (id,))
    # tables = res.fetchone()

    return "OK", 200
