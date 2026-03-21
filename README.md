# Diet Planner

A personal ETL pipeline and Streamlit dashboard for automating diet data collection, meal planning and shopping list generation.

## Overview

This project scrapes meal plans and recipes from a diet portal, stores them in a PostgreSQL database, and exposes a multi-page Streamlit dashboard for browsing recipes, planning weekly menus and generating shopping lists.

## Features

### Admin Panel
- Database statistics — total meals, breakdown by meal type
- One-click scraper trigger to fetch latest recipes from the portal

### Recipe Browser
- Full list of all meals stored in the database
- Detailed view per recipe: preview image, ingredients, macros (protein / carbs / fats / kcal), preparation steps
- Filtering and sorting by meal type, macros, calories

### Diet Planner
- Input your daily calorie and macro targets
- Automatic selection of 8 best-matching recipes per meal type
- Build a full weekly menu by selecting from suggestions
- Generate and download a weekly shopping list as an Excel file

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python, Selenium, BeautifulSoup |
| Database | PostgreSQL, psycopg2, pgAdmin |
| Dashboard | Streamlit |
| Export | openpyxl |
| Config | python-dotenv |
| Environment | WSL / Linux |

## Project Structure

```
diet-planner/
├── db/                  # Database schema and migrations
├── pages/               # Streamlit pages (admin, recipes, planner)
├── src/                 # Core logic: scraper, DB queries, Excel export
├── config.py            # App configuration
├── main.py              # Streamlit entry point
├── .env.example         # Environment variable template
└── requirements.txt
```

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL running locally or via pgAdmin
- Chrome + ChromeDriver (for Selenium)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/hubert-nitka/diet-planner.git
cd diet-planner
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on WSL/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Set up the database schema:
```bash
psql -U your_user -d your_db -f db/schema.sql
```

6. Run the app:
```bash
streamlit run main.py
```

## Database Schema

The database stores meals with full macro information, ingredients, preparation steps and meal type classification. Relationships are defined between meals, ingredients and meal types to support flexible filtering and macro-based matching in the planner.

## Status

Functional — actively used for personal diet planning.
