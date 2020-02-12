from model import Ingredient, connect_to_db, db
from server import app

def load_ingredients():
    """Load ingredients from spoonacular_api_1000.info into ingredients table in database."""
    # Delete rows in ingredients table when we run this file so we won't have duplicates.
    Ingredient.query.delete()

    for row in open("seed_data/spoonacular_api_1000.info"):
        row = row.rstrip()
        ingredient, api_id = row.split(";")

        # Instantiate Ingredient object with information from each row.
        new_ing = Ingredient(name=ingredient, api_id=api_id)
        db.session.add(new_ing)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    load_ingredients()
    