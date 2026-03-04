import unittest
from datetime import datetime
import db


class Item:
    def __init__(self, name, price, cost, wholesale_item):
        self.name = name
        self.price = price
        self.cost = cost
        self.wholesale_item = wholesale_item


class ItemTracker:
    def __init__(self):
        self.storage = {}
        self.items = {}

    def add(self, item, quantity):
        if item.name not in self.storage:
            self.storage[item.name] = quantity
            self.items[item.name] = item
        else:
            self.storage[item.name] += quantity

    def total_value(self):
        total = 0
        for name in self.items:
            total += self.items[name].price * self.storage[name]
        return total

    def display(self):
        for name in self.items:
            print(
                f'{name} - qty: {self.storage[name]}  - $  {self.items[name].price}')


class Inventory(ItemTracker):
    pass


class ShoppingCart(ItemTracker):
    def __init__(self, inventory):
        super().__init__()
        self.inventory = inventory

    def add(self, item, quantity):
        if item.name not in self.inventory.storage:
            print(f'{item.name} not found in inventory.')
            return
        available = self.inventory.storage[item.name]
        if quantity > available:
            print(f'Only {available} in stock.')
            return
        self.inventory.storage[item.name] -= quantity
        if item.name not in self.storage:
            self.storage[item.name] = quantity
            self.items[item.name] = item
        else:
            self.storage[item.name] += quantity

    def remove(self, item, quantity):
        if item.name not in self.storage:
            print(f'{item.name} not in cart.')
            return
        available = self.storage[item.name]
        if quantity > available:
            print(f'Only {available} in cart.')
            return
        self.storage[item.name] -= quantity
        self.inventory.storage[item.name] += quantity
        if self.storage[item.name] == 0:
            del self.storage[item.name]
            del self.items[item.name]


class Category:
    def __init__(self, name):
        self.name = name
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def display_items(self):
        for item in self.items:
            print(f'{item.name} - $ {item.price}')


class Shipping:
    ups_fee = 4.99
    dhl_fee = 6.99

    def __init__(self, provider):
        provider = provider.upper()
        if provider not in ("UPS", "DHL"):
            print("Invalid provider. Choose UPS or DHL.")
            return
        self.provider = provider
        self.fee = self.ups_fee if provider == "UPS" else self.dhl_fee


class PaymentMethod:
    def __init__(self, method, details):
        self.method = method
        self.details = details

    def get_payment(user_type):
        print("1. Card")
        if user_type == "wholesale":
            print("2. Invoice")
        choice = input("Payment method: ").strip()

        if choice == "1":
            card_number = input("Card number: ").strip()
            card_name = input("Name on card: ").strip()
            expiry = input("Expiry: ").strip()
            return PaymentMethod("card", {
                "card_number": card_number,
                "card_name": card_name,
                "expiry": expiry
            })
        elif choice == "2" and user_type == "wholesale":
            company = input("Company name: ").strip()
            org_number = input("Org number: ").strip()
            return PaymentMethod("invoice", {
                "company": company,
                "org_number": org_number
            })
        else:
            print("Invalid choice.")
            return None


class Order:
    def __init__(self, cart, shipping, customer, payment):
        self.cart = cart
        self.shipping = shipping
        self.customer = customer
        self.payment = payment
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
        for name in self.items:
            total += self.item_objects[name].price * self.items[name]
        if self.shipping:
            total += self.shipping.fee
        if self.customer.user_type == "wholesale":
            total *= 0.8
        return round(total, 2)

    def print_receipt(self):
        print("\n--- Receipt ---")
        print(f'Date: {self.order_time}')
        print(f'Customer: {self.customer.name} {self.customer.user_type}')
        print("---")
        for name in self.items:
            qty = self.items[name]
            price = self.item_objects[name].price
            print(f'{name} x{qty} - ${price}')
        print("---")
        if self.shipping:
            print(f'Shipping {self.shipping.provider}: ${self.shipping.fee}')
        if self.customer.user_type == "wholesale":
            print("Wholesale discount: -20%")
        print(f'Total: ${self.total_value()}')
        print("---------------\n")


class Customer:
    def __init__(self, name, email, user_type, address, company_name=""):
        self.name = name
        self.email = email
        self.user_type = user_type  # "guest", "member", "wholesale"
        self.address = address
        self.company_name = company_name
        self.cart = None
        self.orders = []

    def create_cart(self, inventory):
        self.cart = ShoppingCart(inventory)

    def place_order(self, shipping, payment):
        if not self.cart or not self.cart.storage:
            print("Cart is empty.")
            return None
        order = Order(self.cart, shipping, self, payment)
        order.place_order()
        self.orders.append(order)
        return order


# Tests

class TestShoppingCart(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()
        self.item1 = Item("Test Chocolate", 3.95, 0.95, True)
        self.item2 = Item("Test Toffee", 1.95, 0.50, True)
        self.inventory.add(self.item1, 5)
        self.inventory.add(self.item2, 10)
        self.cart = ShoppingCart(self.inventory)

    def test_add(self):
        self.cart.add(self.item1, 3)
        self.assertEqual(self.cart.storage["Test Chocolate"], 3)
        self.assertEqual(self.inventory.storage["Test Chocolate"], 2)

    def test_add_too_many(self):
        self.cart.add(self.item1, 9)
        self.assertNotIn("Test Chocolate", self.cart.storage)
        self.assertEqual(self.inventory.storage["Test Chocolate"], 5)

    def test_remove(self):
        self.cart.add(self.item1, 3)
        self.cart.remove(self.item1, 2)
        self.assertEqual(self.cart.storage["Test Chocolate"], 1)
        self.assertEqual(self.inventory.storage["Test Chocolate"], 4)

    def test_remove_all_clears_cart(self):
        self.cart.add(self.item1, 3)
        self.cart.remove(self.item1, 3)
        self.assertNotIn("Test Chocolate", self.cart.storage)

    def test_remove_item_not_in_cart(self):
        self.cart.remove(self.item1, 1)
        self.assertNotIn("Test Chocolate", self.cart.storage)


def run_shop():
    caramel = Item("Caramel", 1.25, 0.71, True)
    dct = Item("Dark Chocolate Truffles", 2.50, 1.43, True)
    mct = Item("Milk Chocolate Truffles", 1.25, 0.71, True)
    pbc = Item("Peanut Butter Cups", 1.0, 0.57, True)

    member_customer = Customer(
        "Charlie Chonka", "charlie@choc.com", "member", "Cocoa Street 10")
    wholesale_customer = Customer("Willy Wonka", "willy@factory.com",
                                  "wholesale", "Chocolate Lane 123", "Chocolate Factory AB")

    milk = Category("Milk Chocolates")
    dark = Category("Dark Chocolates")
    milk.add_item(caramel)
    milk.add_item(dct)
    dark.add_item(mct)
    dark.add_item(pbc)
    categories = {"1": milk, "2": dark}

    inventory = Inventory()
    inventory.add(caramel, 975)
    inventory.add(dct, 285)
    inventory.add(mct, 881)
    inventory.add(pbc, 995)

    print("Welcome to the Chocolate Shop!")
    print("1. Guest  2. Member  3. Wholesale")
    choice = input("Login: ").strip()

    if choice == "2":
        customer = member_customer
    elif choice == "3":
        customer = wholesale_customer
    else:
        cName = input("Your name: ").strip()
        customer = Customer(cName, "", "guest", "")
        cAddress = input("Your address: ").strip()
        email = input("Your email: ").strip()
        db.add_customer(cName, cAddress, "member", email)


    print(f'Hello {customer.name}!')
    customer.create_cart(inventory)

    while True:
        print("\n1. View items  2. Browse categories  3. Add to cart  4. Remove from cart  5. View cart  6. Checkout  7. Quit")
        action = input("Choose: ").strip()

        if action == "1":
            inventory.display()

        elif action == "2":
            print("1. Milk Chocolates  2. Dark Chocolates")
            cat = input("Category: ").strip()
            if cat in categories:
                categories[cat].display_items()
            else:
                print("Invalid category.")

        elif action == "3":
            inventory.display()
            name = input("Item name: ").strip()
            qty = input("Quantity: ").strip()
            if not qty.isdigit():
                print("Enter a valid number.")
                continue
            item = inventory.items.get(name)
            if item:
                customer.cart.add(item, int(qty))
            else:
                print(f'{name} not found.')

        elif action == "4":
            customer.cart.display()
            name = input("Item to remove: ").strip()
            qty = input("Quantity: ").strip()
            if not qty.isdigit():
                print("Enter a valid number.")
                continue
            item = inventory.items.get(name)
            if item:
                customer.cart.remove(item, int(qty))
            else:
                print(f'{name} not found.')

        elif action == "5":
            if not customer.cart.storage:
                print("Cart is empty.")
            else:
                customer.cart.display()
                print(f'Subtotal: $ {customer.cart.total_value()}')

        elif action == "6":
            if not customer.cart.storage:
                print("Cart is empty.")
                continue
            print("Shipping:  UPS $4.99  |  DHL $6.99")
            ship = input("UPS or DHL: ").strip().upper()
            if ship not in ("UPS", "DHL"):
                print("Invalid choice.")
                continue
            shipping = Shipping(ship)
            payment = PaymentMethod.get_payment(customer.user_type)
            if not payment:
                continue
            order = customer.place_order(shipping, payment)
            if order:
                order.print_receipt()

        elif action == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    run_shop()

    """rows = db.cart_summary()
    for row in rows:
        print(
            f'{row["cName"]} | cartID: {row["cartID"]} | status: {row["status"]} | Quantity: {row["total_quantity"]}')

    print("")

    rows = db.best_selling_items()
    for row in rows:
        print(
            f'{row["item_name"]} | Category: {row["Category"]} | Quantity: {row["total_sold"]}')

    print("")

    rows = db.profit()
    for row in rows:
        print(f'Item: {row["name"]} | Profit: {row["profit"]}')

    rows = db.total_sales_customer()
    for row in rows:
        print(
            f'Customer: {row["customerID"]} | Total spent: {row["total_spent"]}')"""



    #unittest.main()
