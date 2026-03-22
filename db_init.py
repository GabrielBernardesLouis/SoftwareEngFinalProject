import sqlite3

# Define connection and cursor
connection = sqlite3.connect("shop.db")

cursor = connection.cursor()


# =============================================================================
# SCHEMA CREATION
# =============================================================================

# -- 1. Categories ------------------------------------------------------------
# A simple lookup table so products and ingredients can be grouped.
# e.g. "Coffee", "Tea", "Milk", "Syrup", "Food"
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS categories (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE
    )
"""
)

# -- 2. Ingredients (Inventory) -----------------------------------------------
# Raw stock items the shop buys and uses to make drinks.
# e.g. whole milk, oat milk, espresso beans, vanilla syrup, caramel sauce
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS ingredients (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL UNIQUE,
        category_id   INTEGER NOT NULL,
        unit          TEXT    NOT NULL,
        stock_qty     REAL    NOT NULL DEFAULT 0,
        reorder_level REAL    NOT NULL DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
"""
)

# -- 3. Products --------------------------------------------------------------
# Every drink or food item that appears on the menu.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS products (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE,
        category_id INTEGER NOT NULL,
        price       REAL    NOT NULL,
        is_active   INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
"""
)

# -- 4. Product-Ingredient Recipe ---------------------------------------------
# Links each product to the ingredients it consumes and how much.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS product_ingredients (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id    INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        qty_required  REAL    NOT NULL,
        FOREIGN KEY (product_id)    REFERENCES products(id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
        UNIQUE (product_id, ingredient_id)
    )
"""
)

# -- 5. Orders ----------------------------------------------------------------
# One row per customer transaction at the register.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
        total_price  REAL    NOT NULL DEFAULT 0,
        status       TEXT    NOT NULL DEFAULT 'open'
    )
"""
)

# -- 6. Order Items -----------------------------------------------------------
# The individual line items within an order.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id    INTEGER NOT NULL,
        product_id  INTEGER NOT NULL,
        quantity    INTEGER NOT NULL DEFAULT 1,
        unit_price  REAL    NOT NULL,
        FOREIGN KEY (order_id)   REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
"""
)

connection.commit()
print("Database schema created successfully.")


# =============================================================================
# SEED DATA
# =============================================================================

categories = [
    ("Coffee",),
    ("Tea",),
    ("Milk",),
    ("Syrup",),
    ("Food",),
]
cursor.executemany("INSERT OR IGNORE INTO categories (name) VALUES (?)", categories)

# (name, category_name, unit, stock_qty, reorder_level)
ingredients = [
    ("Espresso Beans", "Coffee", "lbs", 10.0, 2.0),
    ("Whole Milk", "Milk", "oz", 256.0, 32.0),
    ("Oat Milk", "Milk", "oz", 128.0, 16.0),
    ("Skim Milk", "Milk", "oz", 128.0, 16.0),
    ("Vanilla Syrup", "Syrup", "pumps", 50.0, 10.0),
    ("Caramel Sauce", "Syrup", "pumps", 50.0, 10.0),
    ("Hazelnut Syrup", "Syrup", "pumps", 50.0, 10.0),
    ("Black Tea Bags", "Tea", "bags", 40.0, 5.0),
    ("Green Tea Bags", "Tea", "bags", 40.0, 5.0),
]
cursor.executemany(
    """
    INSERT OR IGNORE INTO ingredients (name, category_id, unit, stock_qty, reorder_level)
    VALUES (
        ?,
        (SELECT id FROM categories WHERE name = ?),
        ?, ?, ?
    )
""",
    ingredients,
)

# (name, category_name, price)
products = [
    ("Espresso", "Coffee", 2.50),
    ("Latte", "Coffee", 4.75),
    ("Cappuccino", "Coffee", 4.50),
    ("Cold Brew", "Coffee", 4.25),
    ("Vanilla Latte", "Coffee", 5.25),
    ("Caramel Macchiato", "Coffee", 5.50),
    ("Chai Latte", "Tea", 4.50),
    ("Green Tea Latte", "Tea", 4.75),
]
cursor.executemany(
    """
    INSERT OR IGNORE INTO products (name, category_id, price)
    VALUES (
        ?,
        (SELECT id FROM categories WHERE name = ?),
        ?
    )
""",
    products,
)

# (product_name, ingredient_name, qty_required)
recipes = [
    ("Espresso", "Espresso Beans", 0.05),
    ("Latte", "Espresso Beans", 0.05),
    ("Latte", "Whole Milk", 8.0),
    ("Cappuccino", "Espresso Beans", 0.05),
    ("Cappuccino", "Whole Milk", 4.0),
    ("Cold Brew", "Espresso Beans", 0.10),
    ("Vanilla Latte", "Espresso Beans", 0.05),
    ("Vanilla Latte", "Whole Milk", 8.0),
    ("Vanilla Latte", "Vanilla Syrup", 2.0),
    ("Caramel Macchiato", "Espresso Beans", 0.05),
    ("Caramel Macchiato", "Whole Milk", 8.0),
    ("Caramel Macchiato", "Caramel Sauce", 2.0),
    ("Chai Latte", "Black Tea Bags", 1.0),
    ("Chai Latte", "Whole Milk", 8.0),
    ("Green Tea Latte", "Green Tea Bags", 1.0),
    ("Green Tea Latte", "Oat Milk", 8.0),
]
cursor.executemany(
    """
    INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id, qty_required)
    VALUES (
        (SELECT id FROM products    WHERE name = ?),
        (SELECT id FROM ingredients WHERE name = ?),
        ?
    )
""",
    recipes,
)

connection.commit()
print("Seed data inserted successfully.")


# =============================================================================
# CLI DEBUG
# =============================================================================

print("\n--- Menu ---")
cursor.execute(
    """
    SELECT p.name, c.name AS category, p.price
    FROM products p
    JOIN categories c ON c.id = p.category_id
    WHERE p.is_active = 1
    ORDER BY c.name, p.name
"""
)
for row in cursor.fetchall():
    print(f"  {row[1]:<10} {row[0]:<22} ${row[2]:.2f}")

print("\n--- Inventory ---")
cursor.execute(
    """
    SELECT i.name, c.name AS category, i.stock_qty, i.unit, i.reorder_level
    FROM ingredients i
    JOIN categories c ON c.id = i.category_id
    ORDER BY c.name, i.name
"""
)
for row in cursor.fetchall():
    flag = "  <-- LOW STOCK" if row[2] <= row[4] else ""
    print(f"  {row[1]:<8} {row[0]:<22} {row[2]:>6} {row[3]}{flag}")

connection.close()
