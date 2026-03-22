import streamlit as st


st.markdown("""
<style>
div.stButton > button {
    font-size: 12px;
    padding: 4px 6px;
    border-color: #2c1a0e;
    height: 50px;       
    width: 100%; 
    background-color: #242220;
}

.stApp {
    background-color: #361c10
}
</style>
""", unsafe_allow_html=True)

# Menu Data #

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
PUMPS   = ["1", "2", "3", "4", "100%"]

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

def add_item_to_order():
    if not st.session_state.drink:
        return False

    st.session_state.history.append(list(st.session_state.order))

    item = {
        "name":  st.session_state.drink,
        "mods":  build_mod_summary(),
        "price": compute_item_price(),
    }
    st.session_state.order.append(item)

    reset_customizations()
    return True

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
    base          = DRINKS[st.session_state.drink]
    size_upcharge = SIZES[st.session_state.size]
    addon_cost    = sum(ADDONS[a] for a in st.session_state.addons)
    size_default  = SIZE_SHOTS[st.session_state.size]
    extra_shots   = max(0, st.session_state.shots - size_default) * 0.75
    return base + size_upcharge + addon_cost + extra_shots

def reset_customizations():
    st.session_state.drink  = None
    st.session_state.size   = "Medium (12oz)"
    st.session_state.temp   = "Hot"
    st.session_state.milk   = "Whole"
    st.session_state.flavor = "None"
    st.session_state.pumps  = "1"
    st.session_state.shots  = SIZE_SHOTS["Medium (12oz)"]  
    st.session_state.addons = []
    st.session_state.notes  = ""


def undo_last_action():
    if st.session_state.history:
        st.session_state.order = st.session_state.history.pop()


def clear_all_items():
    st.session_state.history.append(list(st.session_state.order))
    st.session_state.order = []


def get_order_subtotal():
    return sum(item["price"] for item in st.session_state.order)


## Front End Layout Start ##

st.markdown("<h1 style='text-align: center;''>Coffee Shop Cafe</h1>", unsafe_allow_html=True)
st.markdown("""---""")

left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown("<h3 style='font-size: 24px; '>Select a Drink</h3>", unsafe_allow_html=True)

    drink_cols = st.columns(4)
    for i, name in enumerate(DRINKS):
        with drink_cols[i % 4]:
            is_selected = st.session_state.drink == name
            if st.button(name, key=f"drink_{name}",
                         use_container_width=True,
                         type="primary" if is_selected else "secondary"):
                st.session_state.drink = name
                st.rerun()
    st.markdown("""---""")

    st.markdown("<h3 style='font-size: 24px; '>Customize</h3>", unsafe_allow_html=True)
    st.caption("Select a drink above to begin")

    size_col, temp_col = st.columns(2)

    with size_col:
        st.caption("Size")

        for size in SIZES:
            is_sel = st.session_state.size == size
            if st.button(size, key=f"size_{size}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.size = size
                st.session_state.shots = SIZE_SHOTS[size]
                st.rerun()
    
    with temp_col:
        st.caption("Temperature")
        for temp in TEMPS:
            is_sel = st.session_state.temp == temp
            if st.button(temp, key=f"temp_{temp}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.temp = temp
                st.rerun()

    st.markdown("""---""")

    milk_col, shots_col = st.columns([2, 1])

    with milk_col:
        st.write("**Milk**")
        milk_cols = st.columns(3)
        for i, milk in enumerate(MILKS):
            with milk_cols[i % 3]:
                is_sel = st.session_state.milk == milk
                if st.button(milk, key=f"milk_{milk}",
                             use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    st.session_state.milk = milk
                    st.rerun()

    with shots_col:
        st.write("**Shots**")
        st.session_state.shots = st.number_input(
            "Shots", min_value=0, max_value=6,
            value=st.session_state.shots,
            label_visibility="collapsed",
            key="shots_input",
        )

    st.markdown("""---""")

    flavor_col, sweet_col = st.columns(2)

    with flavor_col:
        st.write("**Flavor Syrup**")
        for flavor in FLAVORS:
            is_sel = st.session_state.flavor == flavor
            if st.button(flavor, key=f"flavor_{flavor}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.flavor = flavor
                st.rerun()

    with sweet_col:
        st.write("**Pumps**")
        
        st.session_state.shots = st.number_input(
            "Pumps", min_value=0, max_value=6,
            value=st.session_state.shots,
            label_visibility="collapsed",
        )   

    st.markdown("""---""")


    st.write("**Add-ons**")
    addon_cols = st.columns(4)
    for i, (addon, cost) in enumerate(ADDONS.items()):
        with addon_cols[i % 4]:
            checked = addon in st.session_state.addons
            new_val = st.checkbox(f"{addon}  +${cost:.2f}", value=checked, key=f"addon_{addon}")
            if new_val and addon not in st.session_state.addons:
                st.session_state.addons.append(addon)
                st.rerun()
            elif not new_val and addon in st.session_state.addons:
                st.session_state.addons.remove(addon)
                st.rerun()

    st.session_state.notes = st.text_input(
        "Special Instructions",
        value=st.session_state.notes,
        placeholder="e.g. extra hot, no foam, light ice…",
    )

    price = compute_item_price()
    price_col, btn_col = st.columns([2, 1])

    with price_col:
        if st.session_state.drink:
            st.metric("Item Total", f"${price:.2f}")

    with btn_col:
        st.write("") 
        if st.button("＋ Add to Order", key="add_btn",
                     use_container_width=True, type="primary"):
            if add_item_to_order():
                st.toast("✅ Item added!", icon="☕")
                st.rerun()
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
        tax      = subtotal * TAX_RATE
        total    = subtotal + tax

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
            st.rerun()

    with clear_col:
        if st.button("🗑 Clear All", use_container_width=True, key="clear_btn"):
            clear_all_items()
            st.toast("Order cleared.", icon="🗑️")
            st.rerun()
    
    subtotal = get_order_subtotal()
    charge_label = (
        f"💳  Charge  ${subtotal * (1 + TAX_RATE):.2f}"
        if st.session_state.order else "💳  Charge"
    )

    if st.button(charge_label, key="charge_btn",
                 use_container_width=True,
                 type="primary",
                 disabled=not st.session_state.order):
        count = len(st.session_state.order)
        st.session_state.order   = []
        st.session_state.history = []
        st.success(f"✅ Order complete — {count} item(s) charged!")
        st.balloons()
        st.rerun()

st.markdown("""---""")




    