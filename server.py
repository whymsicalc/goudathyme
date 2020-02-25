from flask import Flask, render_template, redirect, request, flash, session, jsonify
from model import connect_to_db, db, User, Ingredient, Item
from jinja2 import StrictUndefined
import os
import psycopg2
import requests

# Delete these two when app is ready to go
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined


app = Flask(__name__)
SECRET_KEY = os.environ['SECRET_KEY']
app.secret_key = SECRET_KEY

app.jinja_env.undefined = StrictUndefined

@app.route("/")
def homepage():
    """Show homepage."""
    return render_template("index.html")


@app.route("/login")
def show_login_page():
    """Show page for user to log in."""
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
    phone = request.form.get("phone")
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
    if session.get("user_id") == None:
        flash("You're not currently logged in!")
        return redirect("/login")
    user = User.query.filter_by(user_id=user_id).first()
    ingredients = Ingredient.query.all()
    items = Item.query.join(Ingredient, Item.ing_id==Ingredient.ing_id).filter(Item.user_id==user_id).order_by(Ingredient.name).all()

    return render_template("my_items.html", user=user, ingredients=ingredients, items=items)


@app.route("/add-to-kitchen", methods=["POST"])
def add_items():
    """Add ingredients to items table in database. If ingredient isn't already in ingredients table, also add to ingredients table."""
    # Get items saved in "ingredients" from my_items.html in list form
    items = request.form.getlist("ingredients")
    items_json =[]
    def create_item(ing_id):
        """Create an Item instance to add to items table."""
        new_item = Item(user_id=session["user_id"], ing_id=ing_id)
        db.session.add(new_item)
        db.session.commit()
        # Append information in a dictionary we need to access in my_items.html to items_json
        items_json.append({"item_id": new_item.item_id,
                                "ingredient_name": new_item.ingredients.name,
                                "expiration_date": new_item.expiration_date,
                                "running_low": new_item.running_low,
                                "notes": new_item.notes,
                                "api_id": new_item.ingredients.api_id
                                })
    # Loop over each item user selected
    for item in items:
        if item.isdigit():
            # Check if item exists in ingredients table
            if Ingredient.query.filter_by(ing_id=item).first() != None:
                # Create Item instance to add to items table if it's not in the user's kitchen yet
                if Item.query.filter_by(user_id=session["user_id"], ing_id=int(item)).first() == None:
                    create_item(int(item))

        # If item isn't an int, it is something the user wrote in:
        else:
            # Create new Ingredient
            new_ing = Ingredient(name=item)
            db.session.add(new_ing)
            db.session.commit()
            create_item(new_ing.ing_id)

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

    items_json = {"ingredient_name": item.ingredients.name,
                                "expiration_date": item.expiration_date,
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
    item_id = request.form.get("item_id")
    low = request.form.get("low")
    if low == "true":
        low = True
    elif low == "false":
        low = False
    item = Item.query.filter_by(item_id=item_id).first()
    item.running_low = low

    db.session.commit()

    return jsonify([])


@app.route("/shopping-list/<int:user_id>")
def show_shopping_list(user_id):
    """Show list of items that user has marked as running low."""
    # import ipdb; ipdb.set_trace()
    if session.get("user_id") == None:
        flash("You're not currently logged in!")
        return redirect("/login")
    user = User.query.filter_by(user_id=user_id).first()
    low_ingredients = Item.query.filter_by(user_id=user_id, running_low=True)
    return render_template("shopping_list.html", user=user, low_ingredients=low_ingredients)


@app.route("/ingredient/<int:api_id>")
def show_ing_info(api_id):
    """Show information on ingredient from Spoonacular API."""
    apiKey = os.environ['apiKey']
    url = "https://api.spoonacular.com/food/ingredients/" + str(api_id) + "/information"
    payload = {'apiKey': apiKey}

    response = requests.get(url, params=payload)
    data = response.json()

    fact_res = requests.get("https://api.spoonacular.com/food/trivia/random", params=payload)
    fact = fact_res.json()['text']

    return render_template("item_info.html", data=data, fact=fact)


if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug
    # DebugToolbar wasn't functioning correctly, so added this line to fix.
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    connect_to_db(app)
    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")

