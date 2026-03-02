import sqlite3

DB_PATH = "chocolate_shop.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


# ---- Items & Inventory ----

def load_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.itemID, i.name, i.price, i.cost, i.wholesale_item, inv.quantity
        FROM Item i
        JOIN Inventory inv ON i.itemID = inv.itemID
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def load_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.categoryID, c.name AS category_name,
               i.name AS item_name, i.price, i.cost, i.wholesale_item
        FROM Category c
        LEFT JOIN Item i ON c.categoryID = i.categoryID
        ORDER BY c.categoryID
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---- Customers ----

def load_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT customerID, cName, email, cAddress, userType, company_name
        FROM Customer
        WHERE userType != 'guest'
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---- Cart ----

def create_cart(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Cart (customerID, createdDate, status)
        VALUES (?, date('now'), 'active')
    """, (customer_id,))
    cart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cart_id


def add_to_cart(cart_id, item_name, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    # Get itemID from name
    cursor.execute("SELECT itemID FROM Item WHERE name = ?", (item_name,))
    row = cursor.fetchone()
    if not row:
        print(item_name + " not found in database.")
        conn.close()
        return

    item_id = row["itemID"]

    # Check if item already in cart
    cursor.execute("""
        SELECT cartLineID, quantity FROM CartLine
        WHERE cartID = ? AND itemID = ?
    """, (cart_id, item_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE CartLine SET quantity = quantity + ?
            WHERE cartLineID = ?
        """, (quantity, existing["cartLineID"]))
    else:
        cursor.execute("""
            INSERT INTO CartLine (cartID, itemID, quantity)
            VALUES (?, ?, ?)
        """, (cart_id, item_id, quantity))

    conn.commit()
    conn.close()


def remove_from_cart(cart_id, item_name, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT itemID FROM Item WHERE name = ?", (item_name,))
    row = cursor.fetchone()
    if not row:
        print(item_name + " not found in database.")
        conn.close()
        return

    item_id = row["itemID"]

    cursor.execute("""
        SELECT cartLineID, quantity FROM CartLine
        WHERE cartID = ? AND itemID = ?
    """, (cart_id, item_id))
    existing = cursor.fetchone()

    if not existing:
        print(item_name + " not in cart.")
        conn.close()
        return

    new_qty = existing["quantity"] - quantity
    if new_qty <= 0:
        cursor.execute("DELETE FROM CartLine WHERE cartLineID = ?", (existing["cartLineID"],))
    else:
        cursor.execute("""
            UPDATE CartLine SET quantity = ?
            WHERE cartLineID = ?
        """, (new_qty, existing["cartLineID"]))

    conn.commit()
    conn.close()


def load_cart(cart_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.name, i.price, cl.quantity
        FROM CartLine cl
        JOIN Item i ON cl.itemID = i.itemID
        WHERE cl.cartID = ?
    """, (cart_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def checkout_cart(cart_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Cart SET status = 'completed'
        WHERE cartID = ?
    """, (cart_id,))
    conn.commit()
    conn.close()


# ---- Complex Queries ----
def best_selling_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.name AS item_name, c.name AS category,
               SUM(ol.quantity) AS total_sold,
               i.price
        FROM Item i
        JOIN Orderline ol ON ol.itemID     = i.itemID
        JOIN Category c   ON c.categoryID = i.categoryID
        GROUP BY i.itemID
        ORDER BY total_sold DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def cart_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ca.cartID, c.cName, ca.createdDate, ca.status,
               COUNT(cl.cartLineID) AS items_in_cart,
               SUM(cl.quantity)     AS total_quantity
        FROM Cart ca
        JOIN Customer c  ON c.customerID  = ca.customerID
        LEFT JOIN CartLine cl ON cl.cartID = ca.cartID
        GROUP BY ca.cartID
        ORDER BY ca.createdDate
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---- Save Order ----

def save_order(customer_id, order):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert into Order
    cursor.execute("""
        INSERT INTO "Order" (customerID, orderDate)
        VALUES (?, ?)
    """, (customer_id, str(order.order_time.date())))
    order_id = cursor.lastrowid

    # Insert each Orderline
    for item_name in order.items:
        quantity = order.items[item_name]
        item = order.item_objects[item_name]
        cursor.execute("""
            SELECT itemID FROM Item WHERE name = ?
        """, (item_name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                INSERT INTO Orderline (orderID, itemID, quantity)
                VALUES (?, ?, ?)
            """, (order_id, row["itemID"], quantity))

    # Insert Payment
    if order.payment:
        cursor.execute("""
            INSERT INTO Payment (orderID, payment_type, payment_date, total_amount)
            VALUES (?, ?, ?, ?)
        """, (
            order_id,
            order.payment.method,
            str(order.order_time.date()),
            order.total_value()
        ))

    conn.commit()
    conn.close()
    print("Order saved to database.")
