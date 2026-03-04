import sqlite3

DB_PATH = "chocolate_shop.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


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


def profit():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, SUM(price-cost) AS profit
        FROM Item 
        GROUP BY itemID
        ORDER BY profit DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


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


def total_sales_customer():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.customerID, SUM(p.total_amount) AS total_spent
        FROM Payment p 
        JOIN "Order" o ON p.orderID = o.orderID
        GROUP BY o.customerID
        ORDER BY total_spent DESC; 
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

def add_customer(name, address, user_type, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Customer (cName, cAddress, userType, email)
        VALUES (?, ?, ?, ?)
    """, (name, address, user_type, email))
    conn.commit()
    conn.close()
    print("Customer added.")