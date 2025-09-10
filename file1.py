from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return"<hi>This Just In:You're an idiot</h1>"

if __name__ == "__main__":
    app.run(debug=True)
