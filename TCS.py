import unittest
from datetime import datetime

class Item:
    def __init__(self, name: str, price: float, cost: float, wholesale_item: bool):
        self.name = name
        self.price = price
        self.cost = cost
        self.wholesale_item = wholesale_item


class ItemTracker:
    def __init__(self):
        self.storage = {}
        self.items = {}

    def add(self, item: Item, quantity: int):
        if item.name not in self.storage:
            self.storage[item.name] = quantity
            self.items[item.name] = item
        else:
            self.storage[item.name] += quantity

    def total_value(self):
        total = 0
        for name in self.items:
            item = self.items[name]
            quantity = self.storage[name]
            total += item.price * quantity
        return total

    def display(self):
        for name in self.items:
            item = self.items[name]
            quantity = self.storage[name]
            print(f"{item.name} - Quantity: {quantity}")

class Inventory(ItemTracker):

    def total_item_price(self, item: Item):
        if item.name not in self.storage:
            return 0
        quantity = self.storage[item.name]
        total = item.price * quantity
        print(f"Total price for {item.name}: {total} $")
        return total


class ShoppingCart(ItemTracker):
    def __init__(self, inventory: Inventory):
        super().__init__()
        self.inventory = inventory

    def add(self, item: Item, quantity: int):
        if item.name in self.inventory.storage:
            available = self.inventory.storage[item.name]

            if quantity <= available:
                self.inventory.storage[item.name] -= quantity

                if item.name not in self.storage:
                    self.storage[item.name] = quantity
                    self.items[item.name] = item
                else:
                    self.storage[item.name] += quantity
            else:
                print(f"Not enough in stock. {available} available.")
        else:
            print(f"'{item.name}' is not available in inventory.")

    def remove(self, item: Item, quantity: int):
        if item.name in self.storage:
            available = self.storage[item.name]

            if quantity <= available:
                self.storage[item.name] -= quantity

                if self.storage[item.name] == 0:
                    del self.storage[item.name]
                    del self.items[item.name]

                self.inventory.storage[item.name] += quantity
            else:
                print(f"Too many to remove. {quantity} available to remove.")

        else:
            print("Item not in cart!")


class Category:
    def __init__(self, name: str):
        self.name = name
        self.items = []

    def add_item(self, item: Item):
        self.items.append(item)

    def display_items(self):
        for item in self.items:
            print(f"{item.name} | {item.price} $")

class Order:
    def __init__(self, cart: ShoppingCart, inventory: Inventory):
        self.cart = cart
        self.inventory = inventory
        self.order_time = None
        self.items = {}
        self.item_objects = {}

    def place_order(self):
        self.items = self.cart.storage.copy()
        self.item_objects = self.cart.items.copy()
        self.order_time = datetime.now()
        self.cart.storage = {}
        self.cart.items = {}

    def total_value(self):
        total = 0
        for item_name, quantity in self.items.items():
            item = self.item_objects[item_name]
            total += item.price * quantity
        return total

    def display_order(self):
        print(f"Order placed at {self.order_time}")
        print(f"Items ordered: ")
        for item_name, quantity in self.items.items():
            item = self.item_objects[item_name]
            print(f"{item_name} | {quantity} | {item.price} $")
        print(f"Total cost: {self.total_value()}$")
        print("")

    def print_receipt(self):
        print("Receipt")
        print(f"Date: {self.order_time}")
        print("--------------------------------------------")
        for item_name, quantity in self.items.items():
            item = self.item_objects[item_name]
            print(f"{item_name} - {quantity}x ${item.price}")
        print("--------------------------------------------")
        print(f"Total: ${self.total_value()}")

class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.orders = []
        self.cart = None

    def create_cart(self, inventory: Inventory):
        self.cart = ShoppingCart(inventory)
        return self.cart

    def place_order(self, inventory: Inventory):
        if not self.cart or not self.cart.storage:
            print("Cart is empty or does not exist.")
            return None
        order = Order(self.cart, inventory)
        order.place_order()
        self.orders.append(order)
        return order

    def display_orders(self):
        if not self.orders:
            print(f"{self.name} has no orders.")
            return
        print(f"Orders for {self.name}:")
        for i, order in enumerate(self.orders, 1):
            print(f"\nOrder #{i}")
            order.display_order()

    def print_last_receipt(self):
        if not self.orders:
            print("No orders placed yet.")
            return
        self.orders[-1].print_receipt()

    def total_spent(self):
        return sum(order.total_value() for order in self.orders)


class TestShoppingCart(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()
        self.shopping_cart = ShoppingCart(self.inventory)

        self.item1 = Item("Test Chocolate", 3.95, 6.95, True)
        self.item2 = Item("Test Toffee", 1.95, 3.95, True)

        self.inventory.add(self.item1, 5)
        self.inventory.add(self.item2, 10)

    def test_add(self):
        self.shopping_cart.add(self.item1, 3)
        self.shopping_cart.add(self.item2, 5)

        self.assertEqual(self.shopping_cart.storage["Test Chocolate"], 3)
        self.assertEqual(self.shopping_cart.storage["Test Toffee"], 5)

        self.assertEqual(self.inventory.storage["Test Chocolate"], 2)
        self.assertEqual(self.inventory.storage["Test Toffee"], 5)

    def test_remove(self):
        self.shopping_cart.add(self.item1, 3)
        self.shopping_cart.add(self.item2, 5)
        self.shopping_cart.remove(self.item1, 2)
        self.shopping_cart.remove(self.item2, 4)

        self.assertEqual(self.shopping_cart.storage["Test Chocolate"], 1)
        self.assertEqual(self.shopping_cart.storage["Test Toffee"], 1)

        self.assertEqual(self.inventory.storage["Test Chocolate"], 4)
        self.assertEqual(self.inventory.storage["Test Toffee"], 9)

    def test_add_too_many(self):
        self.shopping_cart.add(self.item1, 9)

        self.assertNotIn("Test Chocolate", self.shopping_cart.storage)
        self.assertEqual(self.inventory.storage["Test Chocolate"], 5)

if __name__ == "__main__":
    marabou = Item("Marabou", 3.95, 0.95, True)
    fazer = Item("Fazer", 3.50, 0.9, True)
    lindt = Item("Lindt", 6.95, 1.5, True)
    excellanz = Item("Excellanz", 7.95, 1, True)

    milk_chocolates = Category("Milk Chocolates")
    dark_chocolates = Category("Dark Chocolates")

    inventory = Inventory()
    cart = ShoppingCart(inventory)

    milk_chocolates.add_item(marabou)
    milk_chocolates.add_item(fazer)
    dark_chocolates.add_item(lindt)
    dark_chocolates.add_item(excellanz)

    milk_chocolates.display_items()
    dark_chocolates.display_items()

    inventory.add(marabou, 5)
    inventory.add(lindt, 3)

    cart.add(marabou, 2)
    cart.add(lindt, 1)

    order = Order(cart, inventory)
    order.place_order()
    order.display_order()
    order.print_receipt()

    unittest.main()