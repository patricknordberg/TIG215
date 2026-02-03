class Item:
    def __init__(self, name: str, price: float, cost: float, quantity: int, wholesale_item: bool):
        self.name = name
        self.price = price
        self.cost = cost
        self.quantity = quantity
        self.wholesale_item = wholesale_item


class Chocolate(Item):
    def __init__(self, name: str, price: float, cost: float, quantity: int, wholesale_item: bool, flavour: str):
        super().__init__(name, price, cost, quantity, wholesale_item)
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



category = Category("")
category.add_category("Chocolate Specials")
category.add_category("Chocolate Truffles")


print("Categories: ")
category.choose_categories()

chosen_category = input("Choose a category: ")
if chosen_category in category.category_list:
    print("Contents: ")








