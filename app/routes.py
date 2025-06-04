from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from db.connect import connect

bp = Blueprint('main', __name__)

@bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.login"))

#======================================LOGOUT=====================================#

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))

#======================================LOGIN=====================================#

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = connect()
        cur = conn.cursor()
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT userID, password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            user_id, db_password = result
            if password == db_password:
                session['user_id'] = user_id
                flash("Login successful, welcome back", "success")
                cur.close()
                conn.close()
                return redirect(url_for("main.home"))
            else:
                flash("Incorrect password. Please try again.", "error")
        else:
            flash("Username not found. Please register.", "error")
        cur.close()
        conn.close()
    return render_template("login.html")

#======================================REGISTER=====================================#

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = connect()
        cur = conn.cursor()
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash("Username already exists. Please choose a different one or log in instead.")
            cur.close()
            conn.close()
            return redirect(url_for("main.login"))
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("main.login"))
    return render_template("register.html")

#======================================HOME=====================================#

@bp.route("/home", methods=["GET", "POST"])
def home():
    conn = connect()
    cur = conn.cursor()

    if request.method == "POST":
        asset = request.form.get("asset")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        value = float(quantity) * float(price)
        cur.execute(
            "INSERT INTO portfolios (userID, assetName, quantity, price, value) VALUES (%s, %s, %s, %s, %s)",
            (session["user_id"], asset, quantity, price, value)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("main.home"))

    cur.execute(
        "SELECT assetName, quantity, price, value FROM portfolios WHERE userID = %s",
        (session["user_id"],)
    )
    rows = cur.fetchall()
    cur.execute("SELECT username FROM users WHERE userID = %s", (session["user_id"],))
    username = cur.fetchone()[0]

    portfolio = [
        {"assetName": r[0], "quantity": r[1], "price": r[2], "value": r[3]}
        for r in rows
    ]
    
    chart_labels = [item["assetName"] for item in portfolio]
    chart_data = [item["value"] for item in portfolio]

    cur.close()
    conn.close()

    return render_template(
        "home.html",
        username=username,
        portfolio=portfolio,
        chart_labels=chart_labels,
        chart_data=chart_data
    )