from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

portfolioData = []

@app.route("/", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        asset = request.form.get("asset")
        quantity = request.form.get("quantity")
        price = request.form.get("price")

        return redirect(url_for("home"))

    return render_template("home.html", portfolio=portfolioData)

@app.route("/Login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)