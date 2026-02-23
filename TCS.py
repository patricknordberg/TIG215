import unittest
from datetime import datetime


class Item:
    def __init__(self, name, price, cost, wholesale_item):
        self.name = name
        self.price = price
        self.cost = cost
        self.wholesale_item = wholesale_item


# Superclass for both Inventory and ShoppingCart
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
            item = self.items[name]
            quantity = self.storage[name]
            total += item.price * quantity
        return total

    def display(self):
        for name in self.items:
            item = self.items[name]
            quantity = self.storage[name]
            print(item.name + " - Quantity: " + str(quantity))


# Inventory is a subclass of ItemTracker
class Inventory(ItemTracker):

    def total_item_price(self, item):
        if item.name not in self.storage:
            return 0
        quantity = self.storage[item.name]
        total = item.price * quantity
        print("Total price for " + item.name + ": " + str(total) + " $")
        return total


# ShoppingCart is a subclass of ItemTracker
class ShoppingCart(ItemTracker):
    def __init__(self, inventory):
        super().__init__()
        self.inventory = inventory

    def add(self, item, quantity):
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
                print("Not enough in stock. " + str(available) + " available.")
        else:
            print(item.name + " is not available in inventory.")

    def remove(self, item, quantity):
        if item.name in self.storage:
            available = self.storage[item.name]

            if quantity <= available:
                self.storage[item.name] -= quantity

                if self.storage[item.name] == 0:
                    del self.storage[item.name]
                    del self.items[item.name]

                self.inventory.storage[item.name] += quantity
            else:
                print("Too many to remove. " + str(available) + " available to remove.")
        else:
            print("Item not in cart!")


class Category:
    def __init__(self, name):
        self.name = name
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def display_items(self):
        for item in self.items:
            print(item.name + " | " + str(item.price) + " $")


class Shipping:
    ups_fee = 4.99
    dhl_fee = 6.99

    def __init__(self, provider):
        provider = provider.upper()
        if provider != "UPS" and provider != "DHL":
            print("Unknown shipping provider. Choose UPS or DHL.")
            return
        self.provider = provider
        if provider == "UPS":
            self.fee = self.ups_fee
        else:
            self.fee = self.dhl_fee

    def display(self):
        print("Shipping: " + self.provider + " - $" + str(self.fee))


class PaymentMethod:
    def __init__(self, method, details):
        self.method = method  # "card" or "invoice"
        self.details = details

    def get_payment(user_type, customer):
        print("\nPayment options:")
        print("1. Card")
        if user_type == "wholesale":
            print("2. Invoice (wholesale only)")

        choice = input("Choose payment method: ").strip()

        if choice == "1":
            if customer != None and hasattr(customer, "card_details"):
                card = customer.card_details
                print("Card number:  " + card["card_number"])
                print("Name on card: " + card["card_name"])
                print("Expiry:       " + card["expiry"])
                return PaymentMethod("card", card)
            else:
                card_number = input("Card number: ").strip()
                card_name = input("Name on card: ").strip()
                expiry = input("Expiry date: ").strip()
                return PaymentMethod("card", {
                    "card_number": card_number,
                    "card_name": card_name,
                    "expiry": expiry
                })

        elif choice == "2" and user_type == "wholesale":
            company = input("Company name: ").strip()
            org_number = input("Organisation number: ").strip()
            return PaymentMethod("invoice", {
                "company": company,
                "org_number": org_number
            })
        else:
            print("Invalid payment option.")
            return None


class Order:
    def __init__(self, cart, inventory, shipping, customer, payment, personal_details):
        self.cart = cart
        self.inventory = inventory
        self.shipping = shipping
        self.customer = customer
        self.payment = payment
        self.personal_details = personal_details
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
        for item_name in self.items:
            quantity = self.items[item_name]
            item = self.item_objects[item_name]
            total += item.price * quantity
        if self.shipping:
            total += self.shipping.fee
        if self.customer and self.customer.user_type == "wholesale":
            total = total * 0.8
        return round(total, 2)

    def display_order(self):
        print("Order placed at " + str(self.order_time))
        print("Items ordered:")
        for item_name in self.items:
            quantity = self.items[item_name]
            item = self.item_objects[item_name]
            print(item_name + " | " + str(quantity) + " | " + str(item.price) + " $")
        print("Total cost: " + str(self.total_value()) + "$")
        print("")

    def print_receipt(self):
        print("Receipt")
        print("Date: " + str(self.order_time))
        print("--------------------------------------------")
        if self.personal_details:
            print("Name:    " + self.personal_details.get("name", ""))
            print("Email:   " + self.personal_details.get("email", ""))
            print("Address: " + self.personal_details.get("address", ""))
            print("--------------------------------------------")
        for item_name in self.items:
            quantity = self.items[item_name]
            item = self.item_objects[item_name]
            print(item_name + " - " + str(quantity) + "x $" + str(item.price))
        print("--------------------------------------------")
        if self.shipping:
            print("Shipping (" + self.shipping.provider + "): $" + str(self.shipping.fee))
        if self.customer and self.customer.user_type == "wholesale":
            print("Wholesale discount: -20%")
        print("Total: $" + str(self.total_value()))
        print("--------------------------------------------")


class Customer:
    def __init__(self, name, email, user_type, address, company_name):
        self.name = name
        self.email = email
        self.user_type = user_type  # "guest", "member", "wholesale"
        self.address = address
        self.company_name = company_name
        self.orders = []
        self.cart = None

    def create_cart(self, inventory):
        self.cart = ShoppingCart(inventory)
        return self.cart

    def place_order(self, inventory, shipping, payment, personal_details):
        if not self.cart or not self.cart.storage:
            print("Cart is empty.")
            return None
        order = Order(self.cart, inventory, shipping, self, payment, personal_details)
        order.place_order()
        self.orders.append(order)
        return order

    def display_orders(self):
        if not self.orders:
            print(self.name + " has no orders.")
            return
        print("Orders for " + self.name + ":")
        i = 1
        for order in self.orders:
            print("\nOrder #" + str(i))
            order.display_order()
            i += 1

    def print_last_receipt(self):
        if not self.orders:
            print("No orders placed yet.")
            return
        self.orders[-1].print_receipt()

    def total_spent(self):
        total = 0
        for order in self.orders:
            total += order.total_value()
        return total


# ---- Unit Tests ----

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


class TestWholesaleDiscount(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()

        self.item1 = Item("Test Chocolate", 10.00, 5.00, True)
        self.item2 = Item("Test Toffee", 20.00, 10.00, True)

        self.inventory.add(self.item1, 10)
        self.inventory.add(self.item2, 10)

        self.wholesale = Customer("Shajan", "shajan@test.com", "wholesale", "", "")
        self.member = Customer("Dino", "Dino@test.com", "member", "", "")

    def test_wholesale_discount_applied(self):
        self.wholesale.create_cart(self.inventory)
        self.wholesale.cart.add(self.item1, 2)
        shipping = Shipping("UPS")
        order = self.wholesale.place_order(self.inventory, shipping, None, {})
        expected = round((20.00 + 4.99) * 0.8, 2)
        self.assertAlmostEqual(order.total_value(), expected, places=2)

    def test_member_no_discount(self):
        self.member.create_cart(self.inventory)
        self.member.cart.add(self.item2, 1)
        shipping = Shipping("DHL")
        order = self.member.place_order(self.inventory, shipping, None, {})
        expected = round(20.00 + 6.99, 2)
        self.assertAlmostEqual(order.total_value(), expected, places=2)

    def test_wholesale_discount_without_shipping(self):
        self.wholesale.create_cart(self.inventory)
        self.wholesale.cart.add(self.item1, 5)
        order = self.wholesale.place_order(self.inventory, None, None, {})
        expected = round(50.00 * 0.8, 2)
        self.assertAlmostEqual(order.total_value(), expected, places=2)

    def test_wholesale_discount_multiple_items(self):
        self.wholesale.create_cart(self.inventory)
        self.wholesale.cart.add(self.item1, 3)
        self.wholesale.cart.add(self.item2, 2)
        shipping = Shipping("UPS")
        order = self.wholesale.place_order(self.inventory, shipping, None, {})
        expected = round((30.00 + 40.00 + 4.99) * 0.8, 2)
        self.assertAlmostEqual(order.total_value(), expected, places=2)


# ---- Mock Customers ----

member_customer = Customer(
    name="Charlie Chonka",
    email="charlie.chonka@chocolate.com",
    user_type="member",
    address="Cocoa Street 10, 411 38 Gothenburg, Sweden",
    company_name=""
)
member_customer.card_details = {
    "card_number": "**** **** **** 4821",
    "card_name": "Charlie Chonka",
    "expiry": "09/27"
}

wholesale_customer = Customer(
    name="Willy Wonka",
    email="willy.wonka@chocolatefactory.com",
    user_type="wholesale",
    address="Chocolate Lane 123, 423 13 Gothenburg, Sweden",
    company_name="Chocolate Factory AB"
)
wholesale_customer.card_details = {
    "card_number": "**** **** **** 7364",
    "card_name": "Willy Wonka",
    "expiry": "03/26"
}

# ---- End Mock Customers ----


def run_shop():
    marabou = Item("Marabou", 3.95, 0.95, True)
    fazer = Item("Fazer", 3.50, 0.9, True)
    lindt = Item("Lindt", 6.95, 1.5, True)
    excellanz = Item("Excellanz", 7.95, 1, True)

    milk_chocolates = Category("Milk Chocolates")
    dark_chocolates = Category("Dark Chocolates")

    milk_chocolates.add_item(marabou)
    milk_chocolates.add_item(fazer)
    dark_chocolates.add_item(lindt)
    dark_chocolates.add_item(excellanz)

    categories = {"1": milk_chocolates, "2": dark_chocolates}

    inventory = Inventory()
    inventory.add(marabou, 5)
    inventory.add(fazer, 8)
    inventory.add(lindt, 3)
    inventory.add(excellanz, 4)

    print("Welcome to the Chocolate Shop!")
    print("1. Continue as guest")
    print("2. Log in as member")
    print("3. Log in as wholesale user")
    choice = input("Choose: ")

    if choice == "2":
        customer = member_customer
        print("\nHello " + customer.name + "! Logged in as member.")
    elif choice == "3":
        customer = wholesale_customer
        print("\nHello " + customer.name + " (" + customer.company_name + ")! Logged in as wholesale user (20% discount applied at checkout).")
    else:
        customer = Customer("Guest", "", "guest", "", "")
        print("\nContinuing as guest.")

    customer.create_cart(inventory)

    while True:
        print("\nWhat do you want to do?")
        print("1. Browse categories")
        print("2. View all items")
        print("3. Add item to cart")
        print("4. Remove item from cart")
        print("5. View cart")
        print("6. Checkout")
        print("7. Quit")

        action = input("Choose: ")

        if action == "1":
            print("\nCategories:")
            print("1. Milk Chocolates")
            print("2. Dark Chocolates")
            cat_choice = input("Choose a category: ")
            if cat_choice in categories:
                categories[cat_choice].display_items()
            else:
                print("Invalid category.")

        elif action == "2":
            print("\nAll items:")
            for name in inventory.items:
                item = inventory.items[name]
                stock = inventory.storage[name]
                print(item.name + " - $" + str(item.price) + " (in stock: " + str(stock) + ")")

        elif action == "3":
            item_name = input("Enter item name: ")
            quantity = input("Enter quantity: ")

            if not quantity.isdigit():
                print("Quantity must be a number.")
                continue

            quantity = int(quantity)
            item = inventory.items.get(item_name)

            if item:
                customer.cart.add(item, quantity)
            else:
                print(item_name + " not found. Check the spelling.")

        elif action == "4":
            item_name = input("Enter item name to remove: ")
            quantity = input("Enter quantity to remove: ")

            if not quantity.isdigit():
                print("Quantity must be a number.")
                continue

            quantity = int(quantity)
            item = inventory.items.get(item_name)

            if item:
                customer.cart.remove(item, quantity)
            else:
                print(item_name + " not found.")

        elif action == "5":
            if not customer.cart.storage:
                print("Your cart is empty.")
            else:
                print("\nYour cart:")
                for item_name in customer.cart.storage:
                    qty = customer.cart.storage[item_name]
                    item = customer.cart.items[item_name]
                    print(item.name + " - " + str(qty) + "x $" + str(item.price))
                print("Subtotal: $" + str(customer.cart.total_value()))
                print("\nShipping options:")
                print("  UPS - $4.99")
                print("  DHL - $6.99")

        elif action == "6":
            if not customer.cart.storage:
                print("Your cart is empty.")
                continue

            print("\nPersonal details:")
            if customer.user_type != "guest" and customer.name and customer.email:
                print("Name:    " + customer.name)
                print("Email:   " + customer.email)
                print("Address: " + customer.address)
                if customer.user_type == "wholesale" and customer.company_name:
                    print("Company: " + customer.company_name)
                personal_details = {"name": customer.name, "email": customer.email, "address": customer.address}
            else:
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                address = input("Address: ").strip()
                personal_details = {"name": name, "email": email, "address": address}

            print("\nChoose a shipping option:")
            print("  UPS - $4.99")
            print("  DHL - $6.99")
            shipping_choice = input("Enter UPS or DHL: ").strip().upper()
            if shipping_choice != "UPS" and shipping_choice != "DHL":
                print("Invalid shipping option. Please enter UPS or DHL.")
                continue
            shipping = Shipping(shipping_choice)

            payment = PaymentMethod.get_payment(customer.user_type, customer)
            if not payment:
                continue

            order = customer.place_order(inventory, shipping, payment, personal_details)
            if order:
                print()
                order.print_receipt()

        elif action == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    run_shop()
