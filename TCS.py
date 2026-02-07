class Item:
    def __init__(self, name: str, price: float, cost: float, wholesale_item: bool):
        self.name = name
        self.price = price
        self.cost = cost
        self.wholesale_item = wholesale_item


class Inventory:
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




    def total_inventory(self):
        for name in self.items:
            item = self.items[name]
            quantity = self.storage[name]

            print(f"{item.name} | Quantity: {quantity} | Price: {item.price}$")

    def total_item_price(self, item: Item):
        if item.name not in self.storage:
            return 0
        quantity = self.storage[item.name]
        print(f"Total price for {item.name}: {item.price * quantity} $")


class ShoppingCart:
    def __init__(self):
        pass

inventory = Inventory()

#products
print("Inventory: ")

chocolate_bunnies = Item("Chocolate Bunnies", 5.95, 3.40, True)
dark_chocolate_truffles = Item("Dark Chocolate Truffles", 2.50, 1.43, True)
chocolate_cigars = Item("Chocolate Cigars", 50.95, 29.11, True)
caramels = Item("Caramels", 1.25, 0.71, True)
heart_of_chocolate = Item("Heart of Chocolate", 37.95, 21.69, False)


inventory.add(chocolate_bunnies, 20)
inventory.add(dark_chocolate_truffles, 15)
inventory.add(chocolate_cigars, 10)
inventory.add(heart_of_chocolate, 10)
inventory.add(caramels, 80)

inventory.total_inventory()
inventory.total_item_price(chocolate_bunnies)









