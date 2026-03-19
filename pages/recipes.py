import streamlit as st
from pathlib import Path
from src.gendiet import get_all_dishes, get_available_dish_types
from src.utils import clean_img_name
from config import IMGS_FOLDER_WSL

diff_map = {1: "Łatwo", 2: "Średnio", 3: "Trudno"}
prep_map = {1: "Szybko", 2: "Średnio", 3: "Długo"}

def get_wsl_image_path(dish_name):
    clean_name = clean_img_name(dish_name)
    return Path(IMGS_FOLDER_WSL) / f"{clean_name}.png"


st.set_page_config(layout="wide", page_title="Przepisy", page_icon="📖")
st.title("📖 Wszystkie przepisy")

dish_types = get_available_dish_types()

if not dish_types:
    st.warning("Brak danych w bazie.")
    st.stop()

# --- Sidebar: filter, search and sort ---
with st.sidebar:
    st.title("🔍 Filtruj i sortuj")
    selected_type = st.radio("Typ dania:", ["Wszystkie"] + dish_types)
    st.divider()
    search = st.text_input("Szukaj po nazwie:", placeholder="np. kurczak...")
    st.divider()
    sort_by = st.selectbox("Sortuj według:", [
        "Domyślnie", "Kalorie", "Białko", "Węglowodany",
        "Tłuszcz", "Czas przyg.", "Trudność", "Liczba skł.",
    ])
    descending = st.toggle("↓ malejąco", value=False)

# --- Load all dishes from DB (cached) ---
@st.cache_data(ttl=300)
def load_all_dishes():
    return {t: get_all_dishes(dish_type=t) for t in dish_types}

all_dishes = load_all_dishes()

# --- Filter by type ---
if selected_type == "Wszystkie":
    dishes_to_show = [(t, d) for t in dish_types for d in all_dishes.get(t, [])]
else:
    dishes_to_show = [(selected_type, d) for d in all_dishes.get(selected_type, [])]

# --- Filter by name ---
if search:
    dishes_to_show = [(t, d) for t, d in dishes_to_show
                      if search.lower() in d["dish_name"].lower()]

# --- Sort ---
sort_key_map = {
    "Domyślnie":    lambda d: d["dish_name"],
    "Kalorie":      lambda d: d["kcal"],
    "Białko":       lambda d: d["protein_g"],
    "Węglowodany":  lambda d: d["carbs_g"],
    "Tłuszcz":      lambda d: d["fat_g"],
    "Czas przyg.":  lambda d: int(d["prep_time"]),
    "Trudność":     lambda d: int(d["difficulty"]),
    "Liczba skł.":  lambda d: len(d["ingredients"]),
}

# Keep meal type section headers only on default sort with all types visible
group_by_type = (sort_by == "Domyślnie" and selected_type == "Wszystkie")

dishes_to_show = sorted(
    dishes_to_show,
    key=lambda x: (x[0], sort_key_map[sort_by](x[1])) if group_by_type else sort_key_map[sort_by](x[1]),
    reverse=False if group_by_type else descending
)

# --- Display ---
st.caption(f"Znaleziono dań: **{len(dishes_to_show)}**")

if not dishes_to_show:
    st.info("Brak dań spełniających kryteria.")
    st.stop()

current_type = None
for meal_type, dish in dishes_to_show:
    # Show section header when grouping by type
    if group_by_type and meal_type != current_type:
        st.markdown(f"## {meal_type}")
        current_type = meal_type

    p_time  = prep_map.get(int(dish["prep_time"]),  "?")
    d_level = diff_map.get(int(dish["difficulty"]), "?")
    n_ing   = len(dish["ingredients"])
    label = (
        f"{dish['dish_name']}   |   "
        f"🔥 {dish['kcal']} kcal   "
        f"B: {dish['protein_g']}g  W: {dish['carbs_g']}g  T: {dish['fat_g']}g   |   "
        f"🕒 {p_time}  💪 {d_level}  🛒 {n_ing} skł."
    )
    with st.expander(label):
        col1, col2 = st.columns([1, 2])
        with col1:
            wsl_path = get_wsl_image_path(dish["dish_name"])
            if wsl_path.exists():
                st.image(str(wsl_path))
            else:
                st.info("Brak zdjęcia")
            st.markdown("### 👨‍🍳 Przepis")
            st.write(dish["recipe_text"])
        with col2:
            st.markdown(f"**Makro:** B: {dish['protein_g']}g | W: {dish['carbs_g']}g | T: {dish['fat_g']}g")
            st.write(f"🕒 {p_time} | 💪 {d_level} | 🛒 {n_ing} składników")
            st.markdown("### 🛒 Składniki")
            for ing in dish["ingredients"]:
                st.write(f"• {ing['name']} - {ing['qty']} {ing['unit']}")