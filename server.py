from flask import Flask, render_template, redirect, request, flash, session, jsonify
from model import connect_to_db, db, User, Ingredient, Item
from jinja2 import StrictUndefined
from datetime import date, datetime, timedelta
import os
import psycopg2
import requests

# Delete these two when app is ready to go
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

# These two are used for Twilio integration to send texts at a specified time
import schedule
import time
from send_sms import send_reminder_text


app = Flask(__name__)
SECRET_KEY = os.environ['SECRET_KEY']
APIKEY = os.environ['APIKEY']
app.secret_key = SECRET_KEY
# app.debug = True
# app.jinja_env.auto_reload = app.debug
# DebugToolbar wasn't functioning correctly, so added this line to fix.
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.jinja_env.undefined = StrictUndefined

def send_texts():
    users = User.query.all()
    item_lst = []
    # Go through all users
    for user in users:
        # Get items from specified user
        items = Item.query.filter_by(user_id=user.user_id).all()
        # Go through all items from specified user
        for item in items:
            if item.expiration_date:
                # Check if item expires tomorrow (if expiration date minus one day is equal to today)
                if (item.expiration_date + timedelta(days=-1)) == date.today():
                    # If item expires tomorrow, add name of item to item_lst
                    item_lst.append(item.ingredients.name)
        # Make sure item_lst has items in it (if there are expiring items)
        if len(item_lst) >= 1:
            to = user.phone
            # If there is only one expiring item, item_str is string of name of one item
            if len(item_lst) == 1:
                item_str = item_lst[0]
            # If there are multiple items, item_str is comma separated names with an and before last name
            else:
                item_str = ", ".join(item_lst[0:-1]) + " and " + item_lst[-1]
            msg = "Don't forget to eat your " + item_str + " before it expires tomorrow!"
            send_reminder_text(to, msg)


def check_logged_in():
    if session.get("user_id") == None:
        flash("You're not currently logged in!")
        return redirect("/login")


def get_json(url, payload=None):
    """Get JSON from API call to Spoonacular."""
    payload = payload or {}
    payload.update({'apiKey': APIKEY})
    response = requests.get(url, params=payload)
    return response.json()


def create_item(ing_id):
    """Create an Item instance to add to items table."""
    new_item = Item(user_id=session["user_id"], ing_id=ing_id)
    db.session.add(new_item)
    db.session.commit()
    # Append information in a dictionary we need to access in my_items.html to items_json
    return {"item_id": new_item.item_id,
                            "ingredient_name": new_item.ingredients.name,
                            "expiration_date": new_item.expiration_date,
                            "running_low": new_item.running_low,
                            "notes": new_item.notes,
                            "api_id": new_item.ingredients.api_id
                            }


@app.before_first_request
def setup_app():
    """Set up app with these configurations."""

    if not app.config["TESTING"]:
        connect_to_db(app)
        # Use the DebugToolbar
        # DebugToolbarExtension(app)
        # At the same time every day (UTC time), do send_texts()
        schedule.every().day.at("23:00").do(send_texts)
        # Print statement for debugging/to see when setup_app() gets run
        print("start time:", datetime.now())

        # Run continuously as opposed to schedule.run_pending()
        schedule.run_continuously()


@app.route("/")
def homepage():
    """Show homepage."""
    if session.get("user_id") != None:
        user_id = session["user_id"]
        return redirect(f"/my-items/{user_id}")
    return render_template("index.html")


@app.route("/login")
def show_login_page():
    """Show page for user to log in."""
    if session.get("user_id") != None:
        user_id = session["user_id"]
        return redirect(f"/my-items/{user_id}")
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_page():
    """Log in user and return to homepage."""
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            session["user_id"] = user.user_id
            flash("Successfully logged in!")
            return redirect(f"/my-items/{user.user_id}")
        else:
            flash("Incorrect password, please try again.")
            return redirect("/login")
    else:
        flash("No user found with that username. Please register for an account.")
        return redirect("/register")


@app.route("/register")
def show_registration_page():
    """Show page for use to register for an account."""
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_user():
    """Create account for user by adding them to database."""
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    form_phone = request.form.get("phone")
    if form_phone:
        phone_parts = form_phone.split("-")
        phone = "+1" + phone_parts[0] + phone_parts[1] + phone_parts[2]
    else:
        phone = None
    username = request.form.get("username")
    password = request.form.get("password")
    if not User.query.filter_by(username=username).all():
        new_user = User(fname=fname, lname=lname, email=email, phone=phone, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.user_id
        flash("Successfully created an account!")
        return redirect(f"/my-items/{new_user.user_id}")

    else:
        flash("User already exists! Try logging in instead.")
        return redirect("/login")


@app.route("/profile/<int:user_id>")
def show_profile(user_id):
    """Show current user's profile."""
    logged_in = check_logged_in()
    if logged_in:
        return logged_in

    user = User.query.get(user_id)

    return render_template("profile.html", user=user)


@app.route("/update-profile", methods=["POST"])
def update_profile():
    """Update profile with given information."""
    user_id = request.form.get("user_id")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    form_phone = request.form.get("phone")
    if form_phone:
        phone_parts = form_phone.split("-")
        phone = "+1" + phone_parts[0] + phone_parts[1] + phone_parts[2]
    else:
        phone = None

    user = User.query.get(user_id)
    user.fname = fname
    user.lname = lname
    user.email = email
    user.phone = phone
    db.session.commit()

    items_json = {"fname": user.fname,
                "lname": user.lname,
                "email": user.email,
                "phone": user.phone
                }

    return jsonify(items_json)


@app.route("/logout")
def logout_user():
    """Log user out of current session."""
    if session.get("user_id") != None:
        del session["user_id"]
        flash("Successfully logged out!")
        return redirect("/")
    else:
        flash("You're not currently logged in!")
        return redirect("/")


@app.route("/my-items/<int:user_id>")
def show_main_item_page(user_id):
    """Show main page for users to add items and see list of what they currently have."""
    logged_in = check_logged_in()
    if logged_in:
        return logged_in
    user = User.query.get(user_id)
    ingredients = Ingredient.query.all()
    items = Item.query.join(Ingredient, Item.ing_id==Ingredient.ing_id).filter(Item.user_id==user_id).order_by(Ingredient.name).all()
    return render_template("my_items.html", user=user, ingredients=ingredients, items=items)


@app.route("/add-to-kitchen", methods=["POST"])
def add_items():
    """Add ingredients to items table in database. If ingredient isn't already in ingredients table, also add to ingredients table."""
    # Get items saved in "ingredients" from my_items.html in list form
    items = request.form.getlist("ingredients")
    items_json =[]

    # Loop over each item user selected
    for item in items:
        # Check if item exists in ingredients table
        if item.isdigit() and Ingredient.query.get(item) != None:
            # Create Item instance to add to items table if it's not in the user's kitchen yet
            if Item.query.filter_by(user_id=session["user_id"], ing_id=int(item)).first() == None:
                items_json.append(create_item(int(item)))

        # If item isn't an int, it is something the user wrote in:
        else:
            # Create new Ingredient
            new_ing = Ingredient(name=item.lower())
            db.session.add(new_ing)
            db.session.commit()
            items_json.append(create_item(new_ing.ing_id))

    return jsonify(items_json)


@app.route("/update-kitchen", methods=["POST"])
def update_items():
    """Update items in database with information given by user."""
    item_id = request.form.get("item_id")
    date = request.form.get("date")
    low = request.form.get("low")
    if low == "true":
        low = True
    elif low == "false":
        low = False
    notes = request.form.get("notes")
    item = Item.query.filter_by(item_id=item_id).first()
    if len(date) != 0:
        item.expiration_date = date
    item.running_low = low
    item.notes = notes

    db.session.commit()

    if item.expiration_date:
        expiration_date = item.expiration_date.strftime("%A, %B %d, %Y")
    else:
        expiration_date = item.expiration_date
    items_json = {"ingredient_name": item.ingredients.name,
                                "expiration_date": expiration_date,
                                "running_low": item.running_low,
                                "notes": item.notes
                                }

    return jsonify(items_json)


@app.route("/delete-row", methods=["POST"])
def delete_row():
    """Delete item in database with information from given row."""
    item_id = request.form.get("item_id")
    item = Item.query.filter_by(item_id=item_id).first()
    db.session.delete(item)
    db.session.commit()
    # Code kept erroring without a return line, so returning an empty list
    return jsonify([])


@app.route("/update-groceries", methods=["POST"])
def update_running_low():
    """Update running_low for items in database."""
    item_ids = request.form.getlist("item_ids[]")
    for id in item_ids:
        item = Item.query.filter_by(item_id=id).first()
        item.running_low = False
        db.session.commit()
    return jsonify([])


@app.route("/grocery-list/<int:user_id>")
def show_grocery_list(user_id):
    """Show list of items that user has marked as running low."""
    logged_in = check_logged_in()
    if logged_in:
        return logged_in
    user = User.query.get(user_id)
    low_ingredients = Item.query.filter_by(user_id=user_id, running_low=True).all()
    return render_template("grocery_list.html", user=user, low_ingredients=low_ingredients)


@app.route("/ingredient/<int:api_id>")
def show_ing_info(api_id):
    """Show information on ingredient from Spoonacular API."""
    url = "https://api.spoonacular.com/food/ingredients/" + str(api_id) + "/information"
    data = get_json(url)

    fact_url = "https://api.spoonacular.com/food/trivia/random"
    fact = get_json(fact_url)['text']

    return render_template("item_info.html", data=data, fact=fact)


@app.route("/recipe-search/<int:user_id>")
def show_recipe_search(user_id):
    """Show search options for recipes."""
    logged_in = check_logged_in()
    if logged_in:
        return logged_in
    return render_template("recipe_search.html", user_id=user_id)


@app.route("/recipe-search", methods=["POST"])
def search_recipes():
    """Search for recipes based on given criteria."""
    payload = {
        # 'includeIngredients': ingredients,
        'instructionsRequired': 'true',
        'fillIngredients': 'true',
        'addRecipeInformation': 'true',
        'number': 9,
        # 'offset': offset
        }
    user_id = request.form.get("user_id")
    if user_id:
        payload["user_id"] = user_id
    food_type = request.form.get("type")
    if food_type:
        payload["type"] = food_type
    diet = request.form.get("diet")
    if diet:
        payload["diet"] = diet
    cuisine = request.form.get("cuisine")
    if cuisine:
        payload["cuisine"] = cuisine
    intolerances_list = request.form.getlist("intolerances[]")
    intolerances = ",".join(intolerances_list)
    if intolerances:
        payload["intolerances"] = intolerances
    maxReadyTime = request.form.get("maxReadyTime")
    if maxReadyTime:
        payload["maxReadyTime"] = maxReadyTime
    sort = request.form.get("sort")
    if sort:
        payload["sort"] = sort
    # can use to paginate results
    # offset = request.form.get("offset")
    user = User.query.get(user_id)
    items = Item.query.filter(Item.user_id==user_id).all()
    # can set ingredients to search by ingredients
    # Waiting for Spoonacular to update Complex search to implement this
    # ingredient_names = []
    # for item in items:
    #     ingredient_names.append(item.ingredients.name)
    # ingredients = ",".join(ingredient_names)

    url = "https://api.spoonacular.com/recipes/complexSearch"
    payload.update({'apiKey': APIKEY})
    response = requests.get(url, params=payload)
    data = get_json(url, payload)
    return data


@app.route("/recipes/<int:user_id>")
def show_recipes(user_id):
    """Show recipes users can make with ingredients in their kitchen."""
    logged_in = check_logged_in()
    if logged_in:
        return logged_in
    user = User.query.get(user_id)
    items = Item.query.filter(Item.user_id==user_id).all()
    ingredient_names = []
    for item in items:
        ingredient_names.append(item.ingredients.name)
    ingredients = ",".join(ingredient_names)

    url = "https://api.spoonacular.com/recipes/findByIngredients"

    payload = {'ingredients': ingredients,
    'number': 18,
    'ranking': 2}

    data = get_json(url, payload)

    return render_template("recipes.html", data=data, user=user, ingredient_names=ingredient_names, ingredients=ingredients, apiKey=APIKEY)  


@app.route("/original/<int:recipe_id>")
def redirect_to_original_info(recipe_id):
    """Show original website page with recipe information."""
    
    url = "https://api.spoonacular.com/recipes/" + str(recipe_id) + "/information"
    payload = {'includeNutrition': 'false'}
    link = get_json(url, payload)['sourceUrl']

    return redirect(link)


# @app.route("/descriptor", methods=["POST"])
# def retreive_recipe_descriptor():
#     """Get summary of recipe from Spoonacular API"""
#     url = "https://api.spoonacular.com/recipes/" + {id} + "/summary"

# if __name__ == "__main__":
# app.debug = True
# app.jinja_env.auto_reload = app.debug
# # DebugToolbar wasn't functioning correctly, so added this line to fix.
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# connect_to_db(app)
# # Use the DebugToolbar
# DebugToolbarExtension(app)
# app.run(host="0.0.0.0")

# flask run