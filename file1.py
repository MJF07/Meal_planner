from flask import Flask,render_template,request
import csv
from pathlib import Path

app = Flask(__name__)
USERS_CSV = Path(__file__).parent / "users.csv"

@app.route("/")
def index():
    return render_template("index.html",message="Welcome. Please enter your username and password.")
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    print("Username", username)
    print("Password", password)
    with open(USERS_CSV, newline='', encoding="utf-8") as list:
        reader = csv.DictReader(list)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                print("ok")
                return "<h2>Access granted</h2>"
            else:
                return "<h2>Access denied</h2>", 401
if __name__ == "__main__":
    app.run(debug=True)
