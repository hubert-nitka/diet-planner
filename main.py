import json
from src.extract import scrape_diet_plan
from src.utils import log, clear_screen
from config import WEB_USERNAME, WEB_PASSWORD, JSON_PATH

if __name__ == "__main__":

    clear_screen()
    log("=" * 80)
    log("SCRAPING PROCESS STARTED", echo=True)
    log("=" * 80)

    diet_plan = scrape_diet_plan(WEB_USERNAME, WEB_PASSWORD)

    log("Saving results to JSON")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(diet_plan, f, ensure_ascii=False, indent=2)

    log(f"Diet saved to: {JSON_PATH}")
    log("=" * 80)
    log("SCRAPING PROCESS ENDED", echo=True)
    log("=" * 80)