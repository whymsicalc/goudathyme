from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

#Instantiate a SQLAlchemy object to create db.Model classes
db = SQLAlchemy()

class User(db.Model):
    """User model for a user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(16))

    # Association with items table created in Item

    def __repr__(self):
        """Return a readable representation of a Human."""
        return f"<{self.fname} {self.lname}: id={self.user_id}, username={self.username}>"

    def set_password(self, password):
        """Use werkzeug.security's password_hash to securely save password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password given matches hashed password."""
        return check_password_hash(self.password_hash, password)


class Ingredient(db.Model):
    """Ingredient model for an ingredient."""

    __tablename__ = "ingredients"

    ing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    # Considering adding more columns, but not sure what
    # else I need to add yet!

    # Association with items table created in Item

    def __repr__(self):
        """Return a readable representation of a Ingredient."""
        return f"<ing_id={self.ing_id} name={self.name}>"


class Item(db.Model):
    """Item model for an item(ingredient) in kitchens."""

    __tablename__ = "items"

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    ing_id = db.Column(db.Integer, db.ForeignKey("ingredients.ing_id"), nullable=False)
    expiration_date = db.Column(db.DateTime)
    running_low = db.Column(db.Boolean)
    notes = db.Column(db.Text)

    # Create relationship between users table and ingredients table
    ingredients = db.relationship("Ingredient", backref="items")
    users = db.relationship("User", backref="users")

    def __repr__(self):
        """Return a readable representation of an Item in kitchens."""
        return f"<user={self.users.fname} {self.users.lname} ingredient={self.ingredients.name}>"


def connect_to_db(app):
    """Connect the dataase to our Flask app."""

    # Configure to use our database
    # Database URI that should be used for the connection: kitchens
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///kitchens"
    # SQLAlchemy will NOT log all the statements issued to stderr when set to False
    app.config["SQLALCHEMY_ECHO"] = False
    # SQLAlchemy will NOT track modifications of objects
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Connect app with db
    db.app = app
    # Initialize app
    db.init_app(app)


if __name__ == "__main__":
    # If we run file interactively, we can work with database directly.

    from server import app
    connect_to_db(app)

