import streamlit as st
from util.dbHelper import fetch_all

st.markdown("<h1 style='text-align: center;'>Order History</h1>", unsafe_allow_html=True)
st.markdown("---")

# Fetch orders with items
orders = fetch_all("""
    SELECT o.id, o.created_at, o.subtotal, o.tax_amount, o.total_price, o.status,
           GROUP_CONCAT(oi.unit_price || ' - ' || d.name || ' (' || s.name || ')') AS items
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN drinks d ON oi.drink_id = d.id
    JOIN sizes s ON oi.size_id = s.id
    GROUP BY o.id
    ORDER BY o.created_at DESC
""")

if not orders:
    st.info("No orders yet.")
else:
    st.dataframe(
        orders,
        column_config={
            "id": "Order ID",
            "created_at": "Date",
            "subtotal": st.column_config.NumberColumn("Subtotal", format="$%.2f"),
            "tax_amount": st.column_config.NumberColumn("Tax", format="$%.2f"),
            "total_price": st.column_config.NumberColumn("Total", format="$%.2f"),
            "status": "Status",
            "items": "Items"
        },
        width='stretch'
    )