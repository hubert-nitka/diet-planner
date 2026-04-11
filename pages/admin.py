import streamlit as st

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.set_page_config(layout="wide", page_title="Admin", page_icon="🔧")
    st.title("🔒 Dostęp chroniony")
    password = st.text_input("Hasło administratora:", type="password")
    if st.button("Zaloguj"):
        if password == "TWOJE_HASLO_ADMINA":
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Nieprawidłowe hasło!")
    st.stop()

import json
from config import WEB_USERNAME, WEB_PASSWORD, JSON_PATH_DISHES, JSON_PATH_MEALS
from src.extract import scrape_diet_dishes
from src.load import save_dish_to_db
from src.utils import log
from src.gendiet import get_available_dish_types, get_all_dishes

st.set_page_config(layout="wide", page_title="Admin", page_icon="🔧")
st.title("🔧 Panel administracyjny")

# DB stats
@st.cache_data(ttl=60)
def get_db_stats():
    types = get_available_dish_types()
    total = sum(len(get_all_dishes(t)) for t in types)
    return {"types": types, "total": total}

stats = get_db_stats()

st.markdown("### 📊 Aktualny stan bazy")
col1, col2 = st.columns(2)
col1.metric("Łączna liczba dań", stats["total"])
col2.metric("Typy dań", ", ".join(stats["types"]) if stats["types"] else "brak")

st.divider()

# Scraper
st.markdown("### 🔄 Aktualizacja danych")
st.caption("Pobiera nowe dania ze strony trenera, zapisuje do JSON i do bazy danych.")

if st.button("▶️ Uruchom scraper", type="primary"):
    log_lines = []

    with st.spinner("Trwa pobieranie danych ze strony trenera... (może potrwać ok. 30-60 sek.)"):
        try:
            # Scraping
            diet_dishes, diet_meals = scrape_diet_dishes(WEB_USERNAME, WEB_PASSWORD)

            # Saving data to JSON
            with open(JSON_PATH_DISHES, "w", encoding="utf-8") as f:
                json.dump(diet_dishes, f, ensure_ascii=False, indent=2)
            with open(JSON_PATH_MEALS, "w", encoding="utf-8") as f:
                json.dump(diet_meals, f, ensure_ascii=False, indent=2)

            total_scraped = sum(len(v) for v in diet_dishes.items()) if isinstance(diet_dishes, dict) else len(diet_dishes)
            log_lines.append(f"✅ Pobrano dane z serwisu")
            log_lines.append(f"✅ Zapisano JSON: {JSON_PATH_DISHES}")
            log_lines.append(f"✅ Zapisano JSON: {JSON_PATH_MEALS}")

            # DB stats before loading data
            total_before = stats["total"]

            # Save JSON data to DB
            save_dish_to_db(JSON_PATH_DISHES)
            log_lines.append("✅ Baza zaktualizowana")

            # DB stats after loading new data
            types_after = get_available_dish_types()
            total_after = sum(len(get_all_dishes(t)) for t in types_after)
            added   = total_after - total_before
            skipped = max(total_scraped - added, 0)

        except Exception as e:
            st.error(f"❌ Scraper zakończył się błędem: {e}")
            st.stop()

    # Results
    st.success("Scraping zakończony!")
    st.markdown("### 📈 Wyniki")
    c1, c2 = st.columns(2)
    c1.metric("Nowe dania dodane do bazy", added)
    c2.metric("Już istniejące (pominięte)", skipped)

    with st.expander("📋 Szczegółowy log"):
        for line in log_lines:
            st.write(line)

    # Refresh DB stats
    get_db_stats.clear()
    st.rerun()