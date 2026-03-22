import streamlit as st


st.markdown("""
<style>
div.stButton > button {
    font-size: 12px;
    padding: 4px 6px;
}

.stApp {
    background-color: #361c10
}
</style>
""", unsafe_allow_html=True)

# Menu Data #

defaults = {
    "drink":    None,       # Currently selected drink name
    "size":     "Medium (12oz)",
    "temp":     "Hot",
    "milk":     "Whole",
    "flavor":   "None",
    "sweet":    "50%",
    "shots":    2,          # Medium (12oz) default
    "addons":   [],         # List of checked add-on names
    "notes":    "",         # Special instructions text
    "order":    [],         # List of finalized order item dicts
    "history":  [],         # Stack of past order states (used for Undo)
}

DRINKS = {
    "Espresso":      2.50,
    "Latte":         4.25,
    "Pour-over":     4.00,
    "Hot Chocolate": 3.75,
    "Cold Brew":     4.50,
    "Matcha Latte":  4.75,
    "Chai Latte":    4.25,
    "Cappuccino":    4.00,
}

SIZES = {"Small (8oz)": 0.00, "Medium (12oz)": 0.50, "Large (16oz)": 1.00}

SIZE_SHOTS = {"Small (8oz)": 1, "Medium (12oz)": 2, "Large (16oz)": 3}

MILKS       = ["Whole", "Oat", "Almond", "Soy", "Skim", "None"]
TEMPS       = ["Hot", "Iced"]
FLAVORS     = ["None", "Vanilla", "Caramel", "Hazelnut", "Brown Sugar"]
# SWEETNESS   = ["0%", "25%", "50%", "75%", "100%"]

ADDONS = {
    "Extra Shot":       0.75,
    "Cold Foam":        0.75,
    "Whipped Cream":    0.50,
    "Caramel Drizzle":  0.50,
}

TAX_RATE = 0.0625  # 6.25% sales tax

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Front End Layout #

st.markdown("<h1 style='text-align: center;''>Coffee Shop Cafe</h1>", unsafe_allow_html=True)
st.markdown("""---""")

left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown("<h3 style='font-size: 24px; '>Select a Drink</h3>", unsafe_allow_html=True)

    drink_cols = st.columns(4)
    for i, name in enumerate(DRINKS):
        with drink_cols[i % 4]:
            # Highlight the button if this drink is currently selected
            is_selected = st.session_state.drink == name
            if st.button(name, key=f"drink_{name}",
                         use_container_width=True,
                         type="primary" if is_selected else "secondary"):
                st.session_state.drink = name
                st.rerun()

with right:
    st.markdown("<h3 style='font-size: 24px; '>Check out</h3>", unsafe_allow_html=True)
    undo_col, clear_col = st.columns(2)

    with undo_col:
        if st.button("Undo", use_container_width=True, key="undo_btn"):

            st.toast("Last item removed.")
            st.rerun()

    with clear_col:
        if st.button("Clear All", use_container_width=True, key="clear_btn"):

            st.toast("Order cleared.")
            st.rerun()

st.markdown("""---""")


    