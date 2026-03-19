import streamlit as st
 
planner = st.Page("pages/planner.py", title="🥗 Planner", default=True)
recipes = st.Page("pages/recipes.py", title="📖 Przepisy")
admin = st.Page("pages/admin.py", title="🔧 Admin")

pg = st.navigation([planner, recipes, admin])
pg.run()