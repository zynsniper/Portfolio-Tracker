from flask import Flask, flash, render_template, request, redirect, url_for
import psycopg2, os
from db.config import load_config
from db.connect import connect

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

portfolioData = []


@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        asset = request.form.get("asset")
        quantity = request.form.get("quantity")
        price = request.form.get("price")

        return redirect(url_for("home"))

    return render_template("home.html", portfolio=portfolioData)


@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
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
            return redirect(url_for("login"))


        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                    (username, password)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("login"))
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
