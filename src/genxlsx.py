import json
from sqlalchemy import text
from src.utils import connect_to_database

def get_dish_type_id(engine, dish_type):
    """
    Get dish type id for given dish type
    """
    with engine.connect() as conn:
        dish_type_id = conn.execute(
            text(
                """
                SELECT id FROM dish_type
                WHERE type_name = :dish_type
                """
            ),{'dish_type': dish_type}
        )
    return dish_type_id.scalar()

def get_dishes(engine, dish_type, kcal_target, protein_target, carbs_target, fat_target):
    """
    Get best 8 dishes for given meal time based on target kcal, protein, carbs and fat
    """
    kcal_min = int(kcal_target) * 0.8
    kcal_max = int(kcal_target) * 1.3

    with engine.connect() as conn:
        dish_type_id = get_dish_type_id(engine, dish_type)
        result = conn.execute(
            text(
                """
                SELECT *,
                (
                    0.4 * ABS(kcal - :kcal_target) / :kcal_target +

                    0.3 * CASE
                        WHEN :protein_target = 0 THEN protein_g * 0.05
                        ELSE ABS(protein_g - :protein_target) / :protein_target
                    END +

                    0.2 * CASE
                        WHEN :carbs_target = 0 THEN carbs_g * 0.05
                        ELSE ABS(carbs_g - :carbs_target) / :carbs_target
                    END +

                    0.1 * CASE
                        WHEN :fat_target = 0 THEN fat_g * 0.05
                        ELSE ABS(fat_g - :fat_target) / :fat_target
                    END
                ) AS score

                FROM dishes
                WHERE dish_type_id = :dish_type_id
                AND kcal BETWEEN :kcal_min AND :kcal_max

                ORDER BY score ASC
                LIMIT 8
                """
            ),{
                 'kcal_target': kcal_target,
                 'protein_target': protein_target,
                 'carbs_target': carbs_target,
                 'fat_target': fat_target,
                 'dish_type_id': dish_type_id,
                 'kcal_min': kcal_min,
                 'kcal_max': kcal_max
            }
        )

        #Map result as list of dictionaries
        dishes = [row._asdict() for row in result]

    return dishes

########################################
###          MAIN FUNCTIONS          ###
########################################

def generate_diet_proposal(json_file):
    
    engine = connect_to_database()

    try:

        with open(json_file, 'r', encoding='utf-8') as f:
                diet_meals = json.load(f)

        all_dishes = []

        for meal in diet_meals:

            dish_type = meal['meal_type']
            kcal_target = meal['meal_kcal']
            protein_target = meal['meal_proteins']
            carbs_target = meal['meal_carbs']
            fat_target = meal['meal_fats']
            
            best_dishes = get_dishes(engine, dish_type, kcal_target, protein_target, carbs_target, fat_target)

            meal_dishes = {
                'dish_type': dish_type,
                'dishes': best_dishes
            }

            all_dishes.append(meal_dishes)

    finally:
         engine.dispose()

    return all_dishes

