from flask import Flask,render_template,request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html",message="Welcome. Please enter your username and password.")
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    print("Username", username)
    print("Password", password)

    if username == "walter" and password == "mirror":
        return "<h2>Access granted</h2>"
    else:
        return "<h2>Access denied</h2>", 401
if __name__ == "__main__":
    app.run(debug=True)
