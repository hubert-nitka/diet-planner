import json
from src.extract import scrape_diet_dishes
from src.load import save_dish_to_db
from src.utils import log, clear_screen
from src.gendiet import generate_diet_proposal
from config import WEB_USERNAME, WEB_PASSWORD, JSON_PATH_DISHES, JSON_PATH_MEALS

if __name__ == "__main__":
    """
    clear_screen()
    log("=" * 80)
    log("SCRAPING PROCESS STARTED", echo=True)
    log("=" * 80)

    diet_dishes, diet_meals = scrape_diet_dishes(WEB_USERNAME, WEB_PASSWORD)

    log("Saving results to JSON")
    #Save diet dishes json
    with open(JSON_PATH_DISHES, "w", encoding="utf-8") as f:
        json.dump(diet_dishes, f, ensure_ascii=False, indent=2)
    #Save diet meals json
    with open(JSON_PATH_MEALS, "w", encoding="utf-8") as f:
        json.dump(diet_meals, f, ensure_ascii=False, indent=2)

    log(f"Diet dishes saved to: {JSON_PATH_DISHES}")
    log(f"Diet meals saved to: {JSON_PATH_MEALS}")
    log("=" * 80)
    log("SCRAPING PROCESS ENDED", echo=True)
    log("=" * 80)
    """

    diet = generate_diet_proposal(JSON_PATH_MEALS)

    print(diet)