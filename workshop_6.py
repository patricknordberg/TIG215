import sqlite3

class InventoryHandling:
    def __init__(self, db_file):
        self.db_file = db_file

    def change_stock(self, item_id, delta):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        # Update stock
        cur.execute("UPDATE Item SET stock = stock + ? WHERE item_id = ?;", (delta, item_id))
        conn.commit()

        # Remember, we added the CHECK(stock >= 0) when we created the database. It will give an error if this rule is infringed on. You can also add a check at this level to avoid the error from crashing the programme.

        conn.close()

    def low_stock(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT item_id, name, stock, low_level FROM Item WHERE stock <= low_level;")
        rows = cur.fetchall()

        conn.close()
        return rows

    def report_inventory(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("SELECT item_id, name, stock, low_level FROM Item;")
        rows = cur.fetchall()

        conn.close()
        return rows


# Example usage
inv = InventoryHandling("inventory.db")

# Remove 2 notebooks (works)
#inv.change_stock(2, 5)

# Try to remove 1 eraser when stock is 0 (will fail because CHECK(stock >= 0))
#inv.change_stock(3, -1)

print("LOW STOCK:")
for row in inv.low_stock():
    print(row)

print("INVENTORY REPORT:")
for row in inv.report_inventory():
    print(f"ID: {row[0]}, Name: {row[1]}, Stock: {row[2]}, Low Level: {row[3]}")
