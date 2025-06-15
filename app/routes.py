from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from db.connect import connect
import yfinance as yf

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
    stock_info = None
    stock_chart_labels = []
    stock_chart_data = []
    period = request.form.get("period", "1mo")  # Default to 30 days

    if request.method == "POST":
        if "search_stock" in request.form:
            symbol = request.form.get("search_stock").upper()
            period = request.form.get("period", "1mo")
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                price = round(data['Close'].iloc[-1], 2) if not data.empty else None
                stock_info = {
                    "symbol": symbol,
                    "price": price,
                    "name": ticker.info.get("shortName", "N/A")
                }
                if not data.empty:
                    stock_chart_labels = [d.strftime("%Y-%m-%d") for d in data.index]
                    stock_chart_data = [round(p, 2) for p in data['Close']]
            except Exception:
                stock_info = {"symbol": symbol, "price": None, "name": "N/A"}
        else:
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
    total_value = sum(item["value"] for item in portfolio)

    cur.close()
    conn.close()

    return render_template(
        "home.html",
        username=username,
        portfolio=portfolio,
        chart_labels=chart_labels,
        chart_data=chart_data,
        stock_info=stock_info,
        stock_chart_labels=stock_chart_labels,
        stock_chart_data=stock_chart_data,
        period=period,
        total_value=total_value
    )