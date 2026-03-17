"""
Load data gathered by webscraper from Training portal into database
"""
import json
from sqlalchemy import text
from src.utils import connect_to_database, log
    
def get_or_create_dish_type(engine, dish_type):
    """
    Check if dish type already exists in db or create new one if not and return id
    """

    # Check if dish type already exists

    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                SELECT id
                FROM dish_type
                WHERE type_name = :dish_type
                """
            ),{'dish_type': dish_type}
        )
    
        existing_id = result.scalar()

        if existing_id:
            return existing_id
    
    # Insert new dish_type

        result = conn.execute(
            text(
                """
                INSERT INTO dish_type (type_name)
                VALUES (:dish_type)
                RETURNING id
                """
            ),{'dish_type': dish_type}
        )

        return result.scalar()
    
def get_or_create_recipe(engine, dish_name, recipe, img_path, difficulty, prep_time):
    """
    Check if recipe already exists in db or create new one and return id
    """

     # Maps for difficulty and prep time

    diff_map = {
        'Łatwo': 1,
        'Średnio': 2,
        'Trudno': 3
    }

    prep_map = {
        'Szybko': 1,
        'Średnio': 2,
        'Długo': 3
    }

    with engine.begin() as conn:

        # Check if recipe already exists

        result = conn.execute(
            text(
                """
                SELECT id FROM recipes
                WHERE name = :dish_name
                """
            ),{'dish_name': dish_name}
        )

        existing_id = result.scalar()

        if existing_id:
            return existing_id
        
        # Insert new recipe to db

        result = conn.execute(
            text(
                """
                INSERT INTO recipes (name, recipe_text, photo_path, difficulty, prep_time)
                VALUES (:name, :recipe, :photo_path, :difficutly, :prep_time)
                RETURNING id
                """
            ),{
                'name': dish_name,
                'recipe': recipe,
                'photo_path': img_path,
                'difficutly': diff_map.get(difficulty),
                'prep_time': prep_map.get(prep_time)
            }
        )

        return result.scalar()

def get_or_crete_ingredient(engine, ingredient_name):
    """
    Check if ingredient already exists in db, or create it and return id
    """

    with engine.begin() as conn:

        #Check if ingredient already exists
        result = conn.execute(
            text(
                """
                SELECT id FROM ingredients
                WHERE name = :ingredient_name
                """
            ),{'ingredient_name': ingredient_name}
        )
        existing_id = result.scalar()
        if existing_id:
            return existing_id
        
        #Create new ingredient
        result = conn.execute(
            text(
                """
                INSERT INTO ingredients (name)
                VALUES (:ingredient_name)
                RETURNING id
                """
            ),{'ingredient_name': ingredient_name}
        )

        return result.scalar() 


def get_or_create_unit(engine, unit):
    """
    Check if ingredient unit already exists in db or create new one and return id
    """
    # Check if unit already exists
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                SELECT id FROM units
                WHERE name = :unit
                """
            ),{'unit': unit}
        )

        existing_id = result.scalar()

        if existing_id:
            return existing_id
        
        #Create new unit
        result = conn.execute(
            text(
                """
                INSERT INTO units (name)
                VALUES (:unit)
                RETURNING id
                """
            ),{'unit': unit}
        )

        return result.scalar()
    
def get_or_create_dish(engine, recipe_id, kcal, carbs, proteins, fats, dish_type_id):
    with engine.begin() as conn:
        #Check if dish already exists
        result = conn.execute(
            text(
                """
                SELECT id FROM dishes
                WHERE recipe_id = :recipe_id AND kcal = :kcal
                """
            ),{
                'recipe_id': recipe_id,
                'kcal': kcal
            }
        )
        
        existing_id = result.scalar()

        if existing_id:
            return existing_id
        
        #Create new dish
        result = conn.execute(
            text(
                """
                INSERT INTO dishes (recipe_id, kcal, carbs_g, protein_g, fat_g, dish_type_id)
                VALUES (:recipe_id, :kcal, :carbs, :proteins, :fats, :dish_type_id)
                RETURNING id
                """
            ),{
                'recipe_id': recipe_id,
                'kcal': kcal,
                'carbs': carbs,
                'proteins': proteins,
                'fats': fats,
                'dish_type_id': dish_type_id
            }
        )

        return result.scalar()
    


def create_dish_ingredients(engine, ingredients, dish_id):
    """
    Create dish ingredients and return their ids
    """
    with engine.begin() as conn:
        for ingredient in ingredients:
            ingredient_id = get_or_crete_ingredient(engine, ingredient['ingredient_name'])
            unit_id = get_or_create_unit(engine, ingredient['ingredient_unit'])
            conn.execute(
                text(
                    """
                    INSERT INTO dish_ingredients (dish_id, ingredient_id, qty, unit_id)
                    VALUES (:dish_id, :ingredient_id, :qty, :unit_id)
                    """
                ),{
                    'dish_id': dish_id,
                    'ingredient_id': ingredient_id,
                    'qty': ingredient['ingredient_amount'],
                    'unit_id': unit_id
                }
            )

###################################
###        MAIN FUNCTIONS       ###
###################################

def save_dish_to_db(json_file):
    """
    Save dish to db
    """
    
    engine = connect_to_database()

    try:
        # Load data from JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            diet_plan = json.load(f)

        # Iterate through each dish type

        for dish_type, dishes in diet_plan.items():

             # Check if dish type already exists, create if not

            dish_type_id = get_or_create_dish_type(engine, dish_type)

            # Iterate through each dish
            for dish in dishes:

                dish_name = dish['name']
                recipe = dish['instructions']
                img_path = dish['img_path']
                difficulty = dish['difficulty']
                prep_time = dish['prep_time']
                kcal = dish['kcal']
                carbs = dish['carbs']
                proteins = dish['proteins']
                fats = dish['fats']
                ingredients = dish['ingredients']


                # Check if recipe already exists or create new one
                recipe_id = get_or_create_recipe(engine, dish_name, recipe, img_path, difficulty, prep_time)
                
                # Check if dish already exists or create new one
                dish_id = get_or_create_dish(engine, recipe_id, kcal, carbs, proteins, fats, dish_type_id)
                
                # Create dish ingredients
                create_dish_ingredients(engine, ingredients, dish_id)

    finally:
        engine.dispose()