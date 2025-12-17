
from flask import Flask,render_template,request,redirect,url_for,flash
from werkzeug.utils import secure_filename
import csv
from pathlib import Path

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # needed for flash()

BASE_DIR = Path(__file__).parent.resolve()

# === Data directory ===
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# === Users CSV ===
USERS_CSV = DATA_DIR / "users.csv"
USERS_HEADERS = ["username", "password", "email"]
# === Meals CSV ===
CSV_PATH = DATA_DIR / "meals.csv"
CSV_HEADERS = ["name", "prep", "cook"]

# === Recipe CSV (idx -> recipe text + photo filename) ===
RECIPES_CSV = DATA_DIR / "recipes.csv"
RECIPES_HEADERS = ["idx", "recipe", "photo"]

# === Review CSV (idx -> reviews) ===
REVIEWS_CSV = DATA_DIR / "reviews.csv"
REVIEWS_HEADERS = ["idx", "name", "rating", "comment"]

# === Uploads (photos) ===
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}

# ===(plans csv) ===
PLANS_CSV = DATA_DIR / "plans.csv"
PLANS_HEADERS = ["day","slot","meal_idx"]
DAYS=["Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday", "Sunday" ]

# ----------------- CSV helpers ----------------- #
def ensure_users_csv():
    if not USERS_CSV.exists():
        with USERS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=USERS_HEADERS)
            writer.writeheader()

def ensure_meals_csv():
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def ensure_recipes_csv():
    if not RECIPES_CSV.exists():
        with RECIPES_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RECIPES_HEADERS)
            writer.writeheader()


def ensure_reviews_csv():
    if not REVIEWS_CSV.exists():
        with REVIEWS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REVIEWS_HEADERS)
            writer.writeheader()
#def ensure_plan_csv():
    """Create plan.csv with one row per day if it doesn't exist."""
  #  if not PLANS_CSV.exists():
      #  with PLANS_CSV.open("w", newline="", encoding="utf-8") as f:
        #    writer = csv.DictWriter(f, fieldnames=PLANS_HEADERS)
          #  writer.writeheader()
           # for day in DAYS:
             #   writer.writerow({"day": day, "lunch": "", "dinner": ""})

def ensure_plan_csv():
    if not PLANS_CSV.exists():
        with PLANS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=PLANS_HEADERS)
            writer.writeheader()


# ----------- Recipes: load/save text + photo ----------- #

def load_recipe(idx: int) -> str:
    """Return the saved recipe text for this idx, or '' if none."""
    ensure_recipes_csv()
    recipe = ""
    with RECIPES_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("idx") == str(idx):
                recipe = row.get("recipe", "") or ""
    return recipe


def load_photo(idx: int) -> str:
    """Return the saved photo filename for this idx, or '' if none."""
    ensure_recipes_csv()
    photo = ""
    with RECIPES_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("idx") == str(idx):
                photo = row.get("photo", "") or ""
    return photo


def save_recipe(idx: int, text: str | None = None, photo: str | None = None):
    """
    Update or insert one row for this idx.
    If text is not None, update recipe.
    If photo is not None, update photo.
    """
    ensure_recipes_csv()
    rows = []
    found = False

    with RECIPES_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("idx") == str(idx):
                # Update existing row
                if text is not None:
                    row["recipe"] = text
                if photo is not None:
                    row["photo"] = photo
                found = True
            rows.append(row)

    if not found:
        rows.append({
            "idx": str(idx),
            "recipe": text or "",
            "photo": photo or "",
        })

    with RECIPES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RECIPES_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


# ----------------- Reviews helpers ----------------- #

def load_reviews_for_idx(idx: int):
    """Return a list of dicts: {idx, name, rating:int, comment} for this meal idx."""
    ensure_reviews_csv()
    rows = []
    key = str(idx)
    with REVIEWS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("idx") or "").strip() == key:
                name = (row.get("name") or "").strip()
                comment = (row.get("comment") or "").strip()
                try:
                    rating = int(row.get("rating", 0))
                except ValueError:
                    rating = 0
                rows.append({
                    "idx": key,
                    "name": name,
                    "rating": rating,
                    "comment": comment,
                })
    return rows


def append_review_idx(idx: int, name: str, rating: int, comment: str):
    ensure_reviews_csv()
    with REVIEWS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEWS_HEADERS)
        writer.writerow({
            "idx": str(idx),
            "name": (name or "").strip(),
            "rating": str(rating).strip(),
            "comment": (comment or "").strip(),
        })


# ----------------- Meals helpers ----------------- #

def load_meals():
    ensure_meals_csv()
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


def append_meal(name: str, prep: str, cook: str):
    ensure_meals_csv()
    with CSV_PATH.open(mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow({"name": name, "prep": prep, "cook": cook})


MEALS = load_meals()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED
# ----------------- plans helpers ----------------- #
def load_plan():
    """Load weekly plan as a list of dicts with keys: day, lunch, dinner."""
    ensure_plan_csv()
    rows = []
    with PLANS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "day": row.get("day", ""),
                "lunch": row.get("lunch", ""),
                "dinner": row.get("dinner", ""),
            })
    # Ensure all DAYS exist even if file was edited
    existing_days = {r["day"] for r in rows}
    changed = False
    for day in DAYS:
        if day not in existing_days:
            rows.append({"day": day, "lunch": "", "dinner": ""})
            changed = True
    if changed:
        with PLANS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=PLANS_HEADERS)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
    # keep in fixed order
    rows.sort(key=lambda r: DAYS.index(r["day"]))
    return rows

def load_plan_rows():
    ensure_plan_csv()
    rows = []
    with PLANS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_plan_rows(rows):
    ensure_plan_csv()
    with PLANS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLANS_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def plan_by_day(meals):
    """
    Return structure:
    {
      'Monday': {'lunch': [ (idx, meal_name), ... ], 'dinner': [...]},
      ...
    }
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = {d: {"lunch": [], "dinner": []} for d in days}

    for row in load_plan_rows():
        day = row.get("day")
        slot = row.get("slot")
        try:
            meal_idx = int(row.get("meal_idx", "-1"))
        except ValueError:
            continue

        if day not in plan or slot not in ("lunch", "dinner"):
            continue
        if 0 <= meal_idx < len(meals):
            plan[day][slot].append((meal_idx, meals[meal_idx]["name"]))
    return plan


def update_plan_slot(day: str, slot: str, value: str):
    """Update a single slot (lunch/dinner) for a given day with a meal name or ''."""
    ensure_plan_csv()
    day = day.strip()
    if day not in DAYS or slot not in ("lunch", "dinner"):
        return
    rows = []
    with PLANS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("day") == day:
                row[slot] = value
            rows.append(row)
    with PLANS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLANS_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

@app.route("/meal_plan", methods=["GET", "POST"])
def meal_plan():
    global MEALS
    MEALS = load_meals()

    if request.method == "POST":
        action = request.form.get("action", "")
        selected = [int(x) for x in request.form.getlist("selected_meals")]

        rows = load_plan_rows()

        # action formats:
        #   "add:Monday:lunch"
        #   "remove:Monday:lunch:3"   (3 = meal_idx)
        parts = action.split(":")
        if len(parts) >= 3 and parts[0] == "add":
            _, day, slot = parts
            # add ALL selected meals to that day/slot
            for idx in selected:
                rows.append({
                    "day": day,
                    "slot": slot,
                    "meal_idx": str(idx),
                })
            save_plan_rows(rows)

        elif len(parts) >= 4 and parts[0] == "remove":
            _, day, slot, idx_str = parts
            try:
                meal_idx = int(idx_str)
            except ValueError:
                meal_idx = -1

            new_rows = []
            removed_one = False
            for r in rows:
                if (not removed_one and
                    r.get("day") == day and
                    r.get("slot") == slot and
                    r.get("meal_idx") == str(meal_idx)):
                    removed_one = True   # drop this one instance
                    continue
                new_rows.append(r)
            save_plan_rows(new_rows)

    # GET (or after POST) – render page with current plan
    weekly_plan = plan_by_day(MEALS)
    return render_template("meal_plan.html", meals=MEALS, weekly_plan=weekly_plan)
# ----------------- Routes: auth & home ----------------- #

@app.route("/")
def index():
    return render_template(
        "index.html",
        message="Welcome. Please enter your username and password."
    )


@app.route("/login", methods=["POST"])
def login():
    ensure_users_csv()
    username = request.form.get("username")
    password = request.form.get("password")

    with USERS_CSV.open(mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                return render_template("home.html")

    return render_template("wrong_credentials.html")


@app.route("/account_create")
def account_create():
    ensure_users_csv()
    return render_template("account_create.html")


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/forgot_password")
def forgot_password():
    ensure_users_csv()
    return render_template("forgot_password.html")


@app.route("/registration", methods=["POST"])
def registration():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not username or not password or not confirm_password:
        return render_template("account_create.html")

    if password != confirm_password:
        return render_template("ac_wrong_password.html")

    # append to old_users.csv
    with USERS_CSV.open(mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([username, password, email])

    return render_template("confirmation.html")


# ----------------- Cookbook / meals ----------------- #

@app.route("/cookbook", methods=["GET"])
def meals():
    # show list of meals
    return render_template("cookbook.html", meals=MEALS)


@app.route("/add_meal", methods=["POST"])
def add_meal():
    name = (request.form.get("meal_name") or "").strip()
    prep = (request.form.get("prep_time") or "").strip()
    cook = (request.form.get("cook_time") or "").strip()

    if name:
        append_meal(name, prep, cook)
        MEALS.append({"name": name, "prep": prep, "cook": cook})

    return redirect(url_for("meals"))


# ----------------- Meal detail: recipe, photo, reviews ----------------- #

@app.route("/meal/i/<int:idx>", methods=["GET"])
def meal_detail_idx(idx):
    if 0 <= idx < len(MEALS):
        meal = MEALS[idx]
        recipe_text = load_recipe(idx)
        photo_filename = load_photo(idx)
        image_url = None
        if photo_filename:
            image_url = url_for("static", filename=f"uploads/{photo_filename}")

        reviews = load_reviews_for_idx(idx)
        if reviews:
            avg = round(sum(r["rating"] for r in reviews) / len(reviews), 2)
        else:
            avg = 0

        return render_template(
            "meal_detail.html",
            meal=meal,
            recipe_text=recipe_text,
            idx=idx,
            image_url=image_url,
            reviews=reviews,
            avg=avg,
        )
    return "Meal not found", 404


@app.route("/meal/i/<int:idx>/recipe", methods=["POST"])
def meal_save_recipe(idx):
    if not (0 <= idx < len(MEALS)):
        return "Meal not found", 404

    text = (request.form.get("recipe") or "").strip()
    save_recipe(idx, text=text, photo=None)
    return redirect(url_for("meal_detail_idx", idx=idx))


@app.route("/meal/i/<int:idx>/photo", methods=["POST"])
def meal_save_photo(idx):
    if not (0 <= idx < len(MEALS)):
        return "Meal not found", 404

    f = request.files.get("image")
    if not f or f.filename == "":
        flash("Please choose an image.")
        return redirect(url_for("meal_detail_idx", idx=idx))

    if not allowed_file(f.filename):
        flash("Only image files are allowed.")
        return redirect(url_for("meal_detail_idx", idx=idx))

    filename = secure_filename(f.filename)
    f.save(UPLOAD_DIR / filename)

    # store just the filename in recipes.csv
    save_recipe(idx, text=None, photo=filename)
    return redirect(url_for("meal_detail_idx", idx=idx))


@app.route("/meal/i/<int:idx>/review", methods=["POST"])
def meal_add_review(idx):
    if not (0 <= idx < len(MEALS)):
        return "Meal not found", 404

    name = (request.form.get("name") or "").strip()
    comment = (request.form.get("comment") or "").strip()
    try:
        rating = int(request.form.get("rating", "0"))
    except ValueError:
        rating = 0

    if rating < 1 or rating > 5:
        rating = 0

    if rating == 0:
        # Could flash an error message here later
        return redirect(url_for("meal_detail_idx", idx=idx))

    append_review_idx(idx, name, rating, comment)
    return redirect(url_for("meal_detail_idx", idx=idx))


# ----------------- Run app ----------------- #

if __name__ == "__main__":
    app.run(debug=True)