from sqlalchemy import text
from src.utils import connect_to_database
import pandas as pd

def get_dish_id_by_name(meal_plan: dict, dish_name: str) -> int | None:
    for dishes in meal_plan.values():
        for dish in dishes:
            if dish['dish_name'] == dish_name:
                return dish['id']
    return None

def get_dishes(dish_type, kcal_target, protein_target, carbs_target, fat_target, limit=8):
    """
    Get best 8 dishes for given meal time based on target kcal, protein, carbs and fat
    """

    engine = connect_to_database()

    kcal_min = int(kcal_target) * 0.8
    kcal_max = int(kcal_target) * 1.3

    try:
        with engine.connect() as conn:
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

                    FROM full_dishes_view
                    WHERE dish_type = :dish_type
                    AND kcal BETWEEN :kcal_min AND :kcal_max

                    ORDER BY score ASC
                    LIMIT :limit
                    """
                ),{
                    'kcal_target': kcal_target,
                    'protein_target': protein_target,
                    'carbs_target': carbs_target,
                    'fat_target': fat_target,
                    'dish_type': dish_type,
                    'kcal_min': kcal_min,
                    'kcal_max': kcal_max,
                    'limit': limit
                }
            )

            #Map result as list of dictionaries
            dishes = [row._asdict() for row in result]
    finally:
        engine.dispose()
    return dishes

def get_available_dish_types():
    engine = connect_to_database()

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT DISTINCT dish_type FROM full_dishes_view
                    """
                )
            )

        available_types = [row[0] for row in result]
    finally:
        engine.dispose()

    return available_types

def get_all_dishes(dish_type):
    """
    Collects all available dishes from DB based on dish_type
    """
    engine = connect_to_database()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                     SELECT * FROM full_dishes_view
                     WHERE dish_type = :dish_type
                     ORDER BY dish_name
                     """
                ),{"dish_type": dish_type}
            )
            return [row._asdict() for row in result]
    finally:
        engine.dispose()