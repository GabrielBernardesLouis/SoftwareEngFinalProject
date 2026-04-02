import sqlite3

# Define connection and cursor
connection = sqlite3.connect("shop.db")

cursor = connection.cursor()


# =============================================================================
# SCHEMA CREATION
# =============================================================================

# -- 1. Categories ------------------------------------------------------------
cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT    NOT NULL UNIQUE
    )
""")

# -- 2. Drinks ----------------------------------------------------------------
# Matches the DRINKS dict in the frontend exactly.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS drinks (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE,
        base_price  REAL    NOT NULL,
        is_active   INTEGER NOT NULL DEFAULT 1
    )
""")

# -- 3. Sizes -----------------------------------------------------------------
# Matches SIZES and SIZE_SHOTS in the frontend.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sizes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT    NOT NULL UNIQUE,  -- e.g. "Small (8oz)"
        price_add    REAL    NOT NULL DEFAULT 0.00,
        default_shots INTEGER NOT NULL DEFAULT 1
    )
""")

# -- 4. Milks -----------------------------------------------------------------
# Matches MILKS list in the frontend.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS milks (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT    NOT NULL UNIQUE   -- e.g. "Whole", "Oat", "None"
    )
""")

# -- 5. Flavors ---------------------------------------------------------------
# Matches FLAVORS list in the frontend.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS flavors (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT    NOT NULL UNIQUE   -- e.g. "None", "Vanilla", "Caramel"
    )
""")

# -- 6. Add-ons ---------------------------------------------------------------
# Matches ADDONS dict in the frontend.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS addons (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT    NOT NULL UNIQUE,
        price REAL    NOT NULL DEFAULT 0.00
    )
""")

# -- 7. Orders ----------------------------------------------------------------
# One row per customer transaction. Stores tax rate as a snapshot.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
        subtotal    REAL    NOT NULL DEFAULT 0.00,
        tax_rate    REAL    NOT NULL DEFAULT 0.0625,
        tax_amount  REAL    NOT NULL DEFAULT 0.00,
        total_price REAL    NOT NULL DEFAULT 0.00,
        status      TEXT    NOT NULL DEFAULT 'open'  -- open | completed | voided
    )
""")

# -- 8. Order Items -----------------------------------------------------------
# One row per drink in an order, capturing every customization made.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id    INTEGER NOT NULL,
        drink_id    INTEGER NOT NULL,
        size_id     INTEGER NOT NULL,
        milk_id     INTEGER,
        flavor_id   INTEGER,
        shots       INTEGER NOT NULL DEFAULT 2,
        temp        TEXT    NOT NULL DEFAULT 'Hot',   -- 'Hot' or 'Iced'
        notes       TEXT    DEFAULT '',
        unit_price  REAL    NOT NULL,                 -- final price snapshot
        FOREIGN KEY (order_id)  REFERENCES orders(id),
        FOREIGN KEY (drink_id)  REFERENCES drinks(id),
        FOREIGN KEY (size_id)   REFERENCES sizes(id),
        FOREIGN KEY (milk_id)   REFERENCES milks(id),
        FOREIGN KEY (flavor_id) REFERENCES flavors(id)
    )
""")

# -- 9. Order Item Add-ons ----------------------------------------------------
# Separate table because one order item can have multiple add-ons.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_item_addons (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        order_item_id INTEGER NOT NULL,
        addon_id      INTEGER NOT NULL,
        FOREIGN KEY (order_item_id) REFERENCES order_items(id),
        FOREIGN KEY (addon_id)      REFERENCES addons(id),
        UNIQUE (order_item_id, addon_id)
    )
""")

connection.commit()
print("Database schema created successfully.")


# =============================================================================
# SEED DATA  —  mirrors the frontend constants exactly
# =============================================================================

# Categories
cursor.executemany("INSERT OR IGNORE INTO categories (name) VALUES (?)", [
    ("Espresso Drinks",),
    ("Coffee",),
    ("Tea",),
    ("Other",),
])

# Drinks  —  matches DRINKS dict
cursor.executemany("INSERT OR IGNORE INTO drinks (name, base_price) VALUES (?, ?)", [
    ("Espresso",      2.50),
    ("Latte",         4.25),
    ("Pour-over",     4.00),
    ("Hot Chocolate", 3.75),
    ("Cold Brew",     4.50),
    ("Matcha Latte",  4.75),
    ("Chai Latte",    4.25),
    ("Cappuccino",    4.00),
])

# Sizes  —  matches SIZES and SIZE_SHOTS dicts
cursor.executemany("INSERT OR IGNORE INTO sizes (name, price_add, default_shots) VALUES (?, ?, ?)", [
    ("Small (8oz)",   0.00, 1),
    ("Medium (12oz)", 0.50, 2),
    ("Large (16oz)",  1.00, 3),
])

# Milks  —  matches MILKS list
cursor.executemany("INSERT OR IGNORE INTO milks (name) VALUES (?)", [
    ("Whole",),
    ("Oat",),
    ("Almond",),
    ("Soy",),
    ("Skim",),
    ("None",),
])

# Flavors  —  matches FLAVORS list
cursor.executemany("INSERT OR IGNORE INTO flavors (name) VALUES (?)", [
    ("None",),
    ("Vanilla",),
    ("Caramel",),
    ("Hazelnut",),
    ("Brown Sugar",),
])

# Add-ons  —  matches ADDONS dict
cursor.executemany("INSERT OR IGNORE INTO addons (name, price) VALUES (?, ?)", [
    ("Extra Shot",     0.75),
    ("Cold Foam",      0.75),
    ("Whipped Cream",  0.50),
    ("Caramel Drizzle",0.50),
])

connection.commit()
print("Seed data inserted successfully.")


# =============================================================================
# SANITY CHECK
# =============================================================================

print("\n--- Drinks ---")
cursor.execute("SELECT name, base_price FROM drinks WHERE is_active = 1 ORDER BY name")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} ${row[1]:.2f}")

print("\n--- Sizes ---")
cursor.execute("SELECT name, price_add, default_shots FROM sizes ORDER BY price_add")
for row in cursor.fetchall():
    print(f"  {row[0]:<18} +${row[1]:.2f}   {row[2]} shot(s)")

print("\n--- Milks ---")
cursor.execute("SELECT name FROM milks")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print("\n--- Flavors ---")
cursor.execute("SELECT name FROM flavors")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print("\n--- Add-ons ---")
cursor.execute("SELECT name, price FROM addons ORDER BY price DESC")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} ${row[1]:.2f}")

connection.close()