from flask import Flask
import os
from app.routes import bp
from dotenv import load_dotenv

load_dotenv("key.env")
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
