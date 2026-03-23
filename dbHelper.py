import sqlite3
import streamlit as st

# ----------------------
# Cached DB Connection
# ----------------------
DB_NAME = "shop.db"

@st.cache_resource
def get_db_connection():
    """Return a cached SQLite connection for Streamlit."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

# ----------------------
# Execute / Fetch Helpers
# ----------------------
def execute(query, params=()):
    """Execute a query that modifies the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()

def fetch_all(query, params=()):
    """Fetch all rows from a query."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchall()

# ----------------------
# Initialize Database Tables
# ----------------------
def db_init():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            base_price REAL,
            is_active INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price_add REAL,
            default_shots INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS milks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flavors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS addons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtotal REAL,
            tax_rate REAL,
            tax_amount REAL,
            total_price REAL,
            status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            drink_id INTEGER,
            size_id INTEGER,
            milk_id INTEGER,
            flavor_id INTEGER,
            shots INTEGER,
            temp TEXT,
            notes TEXT,
            unit_price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_item_addons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_item_id INTEGER,
            addon_id INTEGER,
            FOREIGN KEY(order_item_id) REFERENCES order_items(id)
        )
    """)
    conn.commit()