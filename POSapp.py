import streamlit as st
from dbHelper import execute, fetch_all, db_init

# Initialize DB (create tables if missing)
db_init()

# ----------------------
# CSS Styling
# ----------------------
st.markdown("""
<style>
div.stButton > button {
    font-size: 12px;
    padding: 4px 6px;
    border-color: #2c1a0e;
    height: 50px;       
    width: 100%; 
    background-color: #242220;
    color: white;
}

.stApp {
    background-color: #361c10;
}

button[kind="primary"] {
    background-color: #d4a373 !important;
    color: black !important;
    border: 2px solid white !important;
}
button[kind="secondary"] {
    opacity: 0.6;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# Defaults and Session State
# ----------------------
defaults = {
    "drink":    None,     
    "size":     "Medium (12oz)",
    "temp":     "Hot",
    "milk":     "Whole",
    "flavor":   "None",
    "pumps":    "1",
    "shots":    2,          
    "addons":   [],         
    "notes":    "",        
    "order":    [],         
    "history":  [],        
}

TEMPS = ["Hot", "Iced"]
PUMPS = ["1", "2", "3", "4", "100%"]

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------------
# Helpers for Button Clicks
# ----------------------
def select_option(key, value):
    st.session_state[key] = value

def set_size(size):
    st.session_state.size = size
    st.session_state.shots = SIZE_SHOTS[size]



# ----------------------
# Load Menu Data from DB
# ----------------------
def load_menu():
    drinks = {name: price for name, price in fetch_all("SELECT name, base_price FROM drinks WHERE is_active = 1")}
    sizes = {name: price for name, price in fetch_all("SELECT name, price_add FROM sizes")}
    size_shots = {name: shots for name, shots in fetch_all("SELECT name, default_shots FROM sizes")}
    milks = [row[0] for row in fetch_all("SELECT name FROM milks")]
    flavors = [row[0] for row in fetch_all("SELECT name FROM flavors")]
    addons = {name: price for name, price in fetch_all("SELECT name, price FROM addons")}
    return drinks, sizes, size_shots, milks, flavors, addons

DRINKS, SIZES, SIZE_SHOTS, MILKS, FLAVORS, ADDONS = load_menu()
TAX_RATE = 0.0625

# ----------------------
# Order Management
# ----------------------
def build_mod_summary():
    parts = [
        st.session_state.size,
        st.session_state.temp,
        f"{st.session_state.milk} milk",
    ]
    if st.session_state.flavor != "None":
        parts.append(f"{st.session_state.flavor} syrup")
    parts.append(f"{st.session_state.pumps} pumps")
    if st.session_state.shots != 1:
        parts.append(f"{st.session_state.shots} shots")
    parts.extend(st.session_state.addons)
    if st.session_state.notes:
        parts.append(f"Note: {st.session_state.notes}")
    return " · ".join(parts)

def compute_item_price():
    if not st.session_state.drink:
        return 0.0
    base = DRINKS[st.session_state.drink]
    size_upcharge = SIZES[st.session_state.size]
    addon_cost = sum(ADDONS[a] for a in st.session_state.addons)
    size_default = SIZE_SHOTS[st.session_state.size]
    extra_shots = max(0, st.session_state.shots - size_default) * 0.75
    return base + size_upcharge + addon_cost + extra_shots

def reset_customizations():
    st.session_state.drink = None
    st.session_state.size = "Medium (12oz)"
    st.session_state.temp = "Hot"
    st.session_state.milk = "Whole"
    st.session_state.flavor = "None"
    st.session_state.pumps = "1"
    st.session_state.shots = SIZE_SHOTS["Medium (12oz)"]
    st.session_state.addons = []
    st.session_state.notes = ""

def add_item_to_order():
    if not st.session_state.drink:
        return False
    st.session_state.history.append(list(st.session_state.order))
    item = {
        "name": st.session_state.drink,
        "size": st.session_state.size,
        "milk": st.session_state.milk,
        "flavor": st.session_state.flavor,
        "shots": st.session_state.shots,
        "temp": st.session_state.temp,
        "addons": list(st.session_state.addons),
        "notes": st.session_state.notes,
        "mods": build_mod_summary(),
        "price": compute_item_price(),
    }
    st.session_state.order.append(item)
    reset_customizations()
    return True

def undo_last_action():
    if st.session_state.history:
        st.session_state.order = st.session_state.history.pop()

def clear_all_items():
    st.session_state.history.append(list(st.session_state.order))
    st.session_state.order = []

def get_order_subtotal():
    return sum(item["price"] for item in st.session_state.order)

# ----------------------
# Save Order to DB
# ----------------------
def save_order_to_db(order_items):
    subtotal = sum(item["price"] for item in order_items)
    tax_rate = TAX_RATE
    tax_amount = subtotal * tax_rate
    total_price = subtotal + tax_amount

    execute("""INSERT INTO orders (subtotal, tax_rate, tax_amount, total_price, status)
               VALUES (?, ?, ?, ?, 'completed')""", (subtotal, tax_rate, tax_amount, total_price))
    order_id = fetch_all("SELECT last_insert_rowid()")[0][0]

    for item in order_items:
        drink_id = fetch_all("SELECT id FROM drinks WHERE name=?", (item["name"],))[0][0]
        size_id = fetch_all("SELECT id FROM sizes WHERE name=?", (item["size"],))[0][0]
        milk_id = fetch_all("SELECT id FROM milks WHERE name=?", (item["milk"],))[0][0]
        flavor_id = fetch_all("SELECT id FROM flavors WHERE name=?", (item["flavor"],))[0][0]

        execute("""INSERT INTO order_items (order_id, drink_id, size_id, milk_id, flavor_id,
                                           shots, temp, notes, unit_price)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (order_id, drink_id, size_id, milk_id, flavor_id, item["shots"], item["temp"], item["notes"], item["price"]))

        order_item_id = fetch_all("SELECT last_insert_rowid()")[0][0]
        for addon in item["addons"]:
            addon_id = fetch_all("SELECT id FROM addons WHERE name=?", (addon,))[0][0]
            execute("""INSERT INTO order_item_addons (order_item_id, addon_id)
                       VALUES (?, ?)""", (order_item_id, addon_id))

# ----------------------
# UI Layout
# ----------------------
st.markdown("<h1 style='text-align: center;'>Coffee Shop Cafe</h1>", unsafe_allow_html=True)
st.markdown("---")

left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown("<h3>Select a Drink</h3>", unsafe_allow_html=True)
    drink_cols = st.columns(4)
    for i, name in enumerate(DRINKS):
        with drink_cols[i % 4]:
            is_selected = st.session_state.drink == name
            st.button(name,
                      key=f"drink_{name}",
                      use_container_width=True,
                      type="primary" if is_selected else "secondary",
                      on_click=select_option,
                      args=("drink", name))

    st.markdown("---")
    st.markdown("<h3>Customize</h3>", unsafe_allow_html=True)
    st.caption("Select a drink above to begin")

    size_col, temp_col = st.columns(2)
    with size_col:
        st.caption("Size")
        for size in SIZES:
            is_sel = st.session_state.size == size
            st.button(size,
                      key=f"size_{size}",
                      use_container_width=True,
                      type="primary" if is_sel else "secondary",
                      on_click=set_size,
                      args=(size,))

    with temp_col:
        st.caption("Temperature")
        for temp in TEMPS:
            is_sel = st.session_state.temp == temp
            st.button(temp,
                      key=f"temp_{temp}",
                      use_container_width=True,
                      type="primary" if is_sel else "secondary",
                      on_click=select_option,
                      args=("temp", temp))

    st.markdown("---")

    milk_col, shots_col = st.columns([2, 1])
    with milk_col:
        st.write("**Milk**")
        milk_cols = st.columns(3)
        for i, milk in enumerate(MILKS):
            with milk_cols[i % 3]:
                is_sel = st.session_state.milk == milk
                st.button(milk,
                          key=f"milk_{milk}",
                          use_container_width=True,
                          type="primary" if is_sel else "secondary",
                          on_click=select_option,
                          args=("milk", milk))

    with shots_col:
        st.write("**Shots**")
        st.session_state.shots = st.number_input("Shots",
                                                 min_value=0,
                                                 max_value=6,
                                                 value=st.session_state.shots,
                                                 label_visibility="collapsed",
                                                 key="shots_input")
    st.markdown("---")

    flavor_col, sweet_col = st.columns(2)
    with flavor_col:
        st.write("**Flavor Syrup**")
        for flavor in FLAVORS:
            is_sel = st.session_state.flavor == flavor
            st.button(flavor,
                      key=f"flavor_{flavor}",
                      use_container_width=True,
                      type="primary" if is_sel else "secondary",
                      on_click=select_option,
                      args=("flavor", flavor))

    with sweet_col:
        st.write("**Pumps**")
        st.session_state.pumps = st.number_input("Pumps",
                                                 min_value=0,
                                                 max_value=6,
                                                 value=int(st.session_state.pumps))

    st.markdown("---")

    st.write("**Add-ons**")
    addon_cols = st.columns(4)
    for i, (addon, cost) in enumerate(ADDONS.items()):
        with addon_cols[i % 4]:
            checked = addon in st.session_state.addons
            new_val = st.checkbox(f"{addon}  +${cost:.2f}", value=checked, key=f"addon_{addon}")
            if new_val and addon not in st.session_state.addons:
                st.session_state.addons.append(addon)
            elif not new_val and addon in st.session_state.addons:
                st.session_state.addons.remove(addon)

    st.session_state.notes = st.text_input("Special Instructions",
                                          value=st.session_state.notes,
                                          placeholder="e.g. extra hot, no foam, light ice…")

    price = compute_item_price()
    price_col, btn_col = st.columns([2, 1])
    with price_col:
        if st.session_state.drink:
            st.metric("Item Total", f"${price:.2f}")
    with btn_col:
        st.write("")
        if st.button("＋ Add to Order", key="add_btn", use_container_width=True, type="primary"):
            if add_item_to_order():
                st.toast("✅ Item added!", icon="☕")
            else:
                st.warning("Please select a drink first.")

with right:
    st.subheader("Current Order")
    if not st.session_state.order:
        st.info("No items yet. Select a drink and add it.")
    else:
        for item in st.session_state.order:
            with st.container(border=True):
                name_col, price_col = st.columns([3, 1])
                with name_col:
                    st.write(f"**{item['name']}**")
                    st.caption(item["mods"])
                with price_col:
                    st.write(f"**${item['price']:.2f}**")

        subtotal = get_order_subtotal()
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        st.divider()
        st.write(f"Subtotal: **${subtotal:.2f}**")
        st.write(f"Tax (6.25%): **${tax:.2f}**")
        st.write(f"### Total: ${total:.2f}")

    st.divider()
    undo_col, clear_col = st.columns(2)
    with undo_col:
        if st.button("↩ Undo", use_container_width=True, key="undo_btn"):
            undo_last_action()
            st.toast("Last item removed.", icon="↩️")
    with clear_col:
        if st.button("🗑 Clear All", use_container_width=True, key="clear_btn"):
            clear_all_items()
            st.toast("Order cleared.", icon="🗑️")

    subtotal = get_order_subtotal()
    charge_label = f"💳  Charge  ${subtotal * (1 + TAX_RATE):.2f}" if st.session_state.order else "💳  Charge"

if st.button(charge_label, key="charge_btn", use_container_width=True, type="primary", disabled=not st.session_state.order):
    save_order_to_db(st.session_state.order)
    count = len(st.session_state.order)
    st.session_state.order = []
    st.session_state.history = []
    st.success(f"✅ Order complete — {count} item(s) charged!")
    st.balloons()