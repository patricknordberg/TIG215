import unittest

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
        print(f"Total price for {item.name}: {item.price * quantity} $")


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
                print(f"Not enough in stock. {quantity} available.")

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





inventory = Inventory()
cart = ShoppingCart(inventory)



#test

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





if __name__ == "__main__":
    unittest.main()









