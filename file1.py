from flask import Flask,render_template,request,redirect,url_for,flash
from werkzeug.utils import secure_filename
import csv
from pathlib import Path

app = Flask(__name__)
USERS_CSV = Path(__file__).parent / "users.csv"
#recipe csv setup
DATA_DIR = Path("data")
#CSV_PATH = DATA_DIR
CSV_PATH = Path(__file__).parent / "data/meals.csv"
CSV_HEADERS = ["name","prep","cook"]
# === Recipe CSV (idx -> recipe text) ===
RECIPES_CSV = DATA_DIR / "recipes.csv"
RECIPES_HEADERS = ["idx", "recipe", "photo"]
#photo directory goes here
PHOTOS_DIR=Path("photos")
###################################
BASE_DIR = Path(__file__).parent.resolve()
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}

###############################
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

    return render_template('wrong_credentials.html')

@app.route("/account_create")
def account_create():
    return render_template("account_create.html")
@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/meal_plan",methods=["POST","GET"])
def meal_plan():
    return render_template("meal_plan.html")
@app.route("/meal_requests")
def meal_requests():
    return render_template("meal_requests.html")
@app.route("/profile-rating.html")
def profile_rating():
    return render_template("profile-rating.html")
@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/registration", methods=["POST"])
def registration():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if not username or not password or not password or not confirm_password:
        return render_template("account_create.html")
    if password!=confirm_password:
        return render_template("ac_wrong_password.html")

    with open("users.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            ## return render_template("ac_wrong_password.html")
            writer.writerow([username,password,email])  # writes all rows at once
    print("users.csv written successfully!")
    print(email)
    print(username)
    print(password)
    print(confirm_password)
    return render_template("confirmation.html")

#these are functions to read from the recipes
def load_recipe(idx: int) -> str:
    """Return the saved recipe text for this idx, or '' if none."""
   # ensure_recipes_csv()
    recipe = ""
    with RECIPES_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("idx") == str(idx):
                recipe = row.get("recipe", "")
    print(recipe)
    return recipe
#This will save the recipe
def save_recipe(idx: int, text: str, photo:str):
    """Overwrite/insert one row for this idx."""
    #ensure_recipes_csv()
    rows = []
    found = False
    # read all rows
    with RECIPES_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("idx") == str(idx) and text !=None:
                rows.append({"idx": str(idx), "recipe": text})
                found = True
#leaving off here for thanksgiving
            if row.get("idx") == str(idx) and photo !=None:
                rows.append({"idx": str(idx), "photo": photo})
                found = True
            else:
                rows.append(row)
    # write back (replace or append)
    with RECIPES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RECIPES_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        if not found:
            writer.writerow({"idx": str(idx), "recipe": text, "photo": photo})

#saves recipes on the meal_detail pages
@app.route("/meal/i/<int:idx>/recipe", methods=["POST"])
def meal_save_recipe(idx):
    if not (0 <= idx < len(MEALS)):
        return "Meal not found", 404
    text = (request.form.get("recipe") or "").strip()
    save_recipe(idx, text, photo=None)
    return redirect(url_for("meal_detail_idx", idx=idx))
#add photos
#######################################
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

@app.route("/meal/i/<int:idx>/photo", methods=["POST"])
def meal_save_photo(idx):
    print("this is save photos")
    f = request.files.get("image")
    if not f or f.filename == "":
        flash("Please choose an image.")
        return redirect(url_for("form"))
    if not allowed_file(f.filename):
        flash("Only image files are allowed.")
        return redirect(url_for("form"))

    filename = secure_filename(f.filename)
    f.save(UPLOAD_DIR / filename)
    image_url = url_for("static", filename=f"uploads/{filename}")
    print(filename)
    save_recipe(idx,text=None,photo=filename)
    return render_template("meal_detail.html", meal=MEALS,idx=idx,image_url=image_url, filename=filename)

#####################################
#add meals to cookbook?
def load_meals():
  #  ensure_csv()
    meals = []
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            meals.append({
                "name": row.get("name", "").strip(),
                "prep": row.get("prep", "").strip(),
                "cook": row.get("cook", "").strip(),
            })
    return meals

def append_meal(name:str, prep:str, cook:str):
    #ensure_csv
    with CSV_PATH.open(mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=CSV_HEADERS)
        writer.writerow({"name": name, "prep": prep, "cook": cook})
MEALS = load_meals()
@app.route("/cookbook",methods=["GET"])
def meals(): #name should be cookbook
    return render_template("cookbook.html", meals=MEALS)
@app.route("/meal/i/<int:idx>",methods=["GET"])
def meal_detail_idx(idx):
    if 0<=idx<len(MEALS):
        meal=MEALS[idx]
        recipe_text=load_recipe(idx)
        return render_template("meal_detail.html", meal=meal, recipe_text=recipe_text, idx=idx)
    return"meal not found",404
@app.route("/add_meal", methods=["POST"])
def add_meal():
    name = (request.form.get("meal_name") or "").strip()
    prep = (request.form.get("prep_time") or "").strip()
    cook = (request.form.get("cook_time") or "").strip()

    if name:
        append_meal(name, prep, cook)
        MEALS.append({"name": name, "prep": prep, "cook": cook})
    return redirect (url_for("meals"))

if __name__ == "__main__":
    app.run(debug=True)
