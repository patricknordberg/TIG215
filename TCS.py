class Item:
    def __init__(self, name: str, price: float, cost: float, wholesale_item: bool):
        self.name = name
        self.price = price
        self.cost = cost
        self.wholesale_item = wholesale_item



class Chocolate(Item):
    def __init__(self, name: str, price: float, cost: float, wholesale_item: bool, flavour: str):
        super().__init__(name, price, cost, wholesale_item)
        self.flavour = flavour




class Category:
    def __init__(self, name: str):
        self.name = name
        self.category_list = []


    def choose_categories(self):
        for c in self.category_list:
            print(c.name)

    def add_category(self, name: str):
        self.category_list.append(Category(name))


class Inventory:
    def __init__(self):
        self.storage = {}

    def add_in_inventory(self, item: Item, quantity: int):
        if item.name not in self.storage:
            self.storage[item.name] = {"item": item, "quantity": 0}
        self.storage[item.name]["quantity"] += quantity


    def total_inventory(self):
        for name, data in self.storage.items():
            item = data["item"]
            quantity = data["quantity"]
            print(f"{item.name} | Quantity: {quantity} | Price: {item.price}$")

category = Category("")
inventory = Inventory()

#products
chocolate_bunnies = Item("Chocolate Bunnies", 5.95, 3.40, True)
dark_chocolate_truffles = Item("Dark Chocolate Truffles", 2.50, 1.43, True)
chocolate_cigars = Item("Chocolate Cigars", 50.95, 29.11, True)
caramels = Item("Caramels", 1.25, 0.71, True)
heart_of_chocolate = Item("Heart of Chocolate", 37.95, 21.69, False)


inventory.add_in_inventory(chocolate_bunnies, 20)
inventory.add_in_inventory(dark_chocolate_truffles, 15)
inventory.add_in_inventory(chocolate_cigars, 10)
inventory.add_in_inventory(heart_of_chocolate, 10)
inventory.add_in_inventory(caramels, 80)

inventory.total_inventory()

category.choose_categories()









