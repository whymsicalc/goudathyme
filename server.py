from flask import Flask, render_template, redirect, request, flash, session
from model import connect_to_db, db, User, Ingredient, Item
from jinja2 import StrictUndefined
import os
import psycopg2

app = Flask(__name__)
SECRET_KEY = os.environ['SECRET_KEY']
app.secret_key = SECRET_KEY

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
            session["username"] = username
            flash("Successfully logged in!")
            return redirect("/")
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

        flash("Successfully created an account!")
        return redirect("/")

    else:
        flash("User already exists! Try logging in instead.")
        return redirect("/login")



if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    app.jinja_env.auto_reload = app.debug
    app.run(host="0.0.0.0")