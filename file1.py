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
    with open("users.csv", mode='r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            if row['username'] == username and row['password'] == password:
                print("ok")
                return render_template('home.html')

    return render_template('index.html')

@app.route("/account_create")
def account_create():
    return render_template("account_create.html")
@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/cookbook")
def cookbook():
    return render_template("cookbook.html")
@app.route("/meal_plan",methods=["POST","GET"])
def meal_plan():
    return render_template("meal_plan.html")
@app.route("/meal_requests")
def meal_requests():
    return render_template("meal_requests.html")



@app.route("/registration", methods=["POST"])
def registration():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    with open("users.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([username,password,email])  # writes all rows at once

    print("users.csv written successfully!")
    print(email)
    print(username)
    print(password)
    print(confirm_password)
    return render_template("confirmation.html")



if __name__ == "__main__":
    app.run(debug=True)
