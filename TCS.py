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

class Shipping:
    OPTIONS = {
        "UPS": 4.99,
        "DHL": 6.99,
    }

    def __init__(self, provider: str):
        provider = provider.upper()
        if provider not in self.OPTIONS:
            raise ValueError(f"Unknown shipping provider: {provider}. Choose UPS or DHL.")
        self.provider = provider
        self.fee = self.OPTIONS[provider]

    def display(self):
        print(f"Shipping: {self.provider} - ${self.fee}")


class PaymentMethod:
    def __init__(self, method: str, details: dict):
        self.method = method  # "card" or "invoice"
        self.details = details

    @staticmethod
    def from_input(user_type: str):
        print("\nPayment options:")
        print("1. Card")
        if user_type == "wholesale":
            print("2. Invoice (wholesale only)")

        choice = input("Choose payment method: ").strip()

        if choice == "1":
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
    def __init__(self, cart: ShoppingCart, inventory: Inventory, shipping: Shipping = None, customer: "Customer" = None, payment: PaymentMethod = None, personal_details: dict = None):
        self.cart = cart
        self.inventory = inventory
        self.shipping = shipping
        self.customer = customer
        self.payment = payment
        self.personal_details = personal_details or {}
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
        if self.shipping:
            total += self.shipping.fee
        if self.customer and self.customer.user_type == "wholesale":
            total = total * 0.8
        return round(total, 2)

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
        if self.personal_details:
            print(f"Name:    {self.personal_details.get('name', '')}")
            print(f"Email:   {self.personal_details.get('email', '')}")
            print(f"Address: {self.personal_details.get('address', '')}")
            print("--------------------------------------------")
        for item_name, quantity in self.items.items():
            item = self.item_objects[item_name]
            print(f"{item_name} - {quantity}x ${item.price}")
        print("--------------------------------------------")
        if self.shipping:
            print(f"Shipping ({self.shipping.provider}): ${self.shipping.fee}")
        if self.customer and self.customer.user_type == "wholesale":
            print("Wholesale discount: -20%")
        print(f"Total: ${self.total_value()}")
        print("--------------------------------------------")


class Customer:
    def __init__(self, name: str, email: str, user_type: str = "guest", address: str = "", company_name: str = ""):
        self.name = name
        self.email = email
        self.user_type = user_type  # "guest", "member", "wholesale"
        self.address = address
        self.company_name = company_name
        self.orders = []
        self.cart = None

    def create_cart(self, inventory: Inventory):
        self.cart = ShoppingCart(inventory)
        return self.cart

    def place_order(self, inventory: Inventory, shipping: Shipping = None, payment: PaymentMethod = None, personal_details: dict = None):
        if not self.cart or not self.cart.storage:
            print("Cart is empty or does not exist.")
            return None
        order = Order(self.cart, inventory, shipping, customer=self, payment=payment, personal_details=personal_details)
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


# --- Mock Customers ---

member_customer = Customer(
    name="Charlie",
    email="charlie@email.com",
    user_type="member",
    address="Candystreet 123"
)

wholesale_customer = Customer(
    name="Willy Wonka",
    email="chocolatefactory@email.com",
    user_type="wholesale",
    address="Candy City 123",
    company_name="ChocolateFactory"
)

# --- End Mock Customers ---


def run_shop():
    # setup items
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

    # login or guest
    print("Welcome to the Chocolate Shop!")
    print("1. Continue as guest")
    print("2. Log in as member")
    print("3. Log in as wholesale user")
    choice = input("Choose: ")

    if choice == "2":
        customer = member_customer
        print(f"\nHello {customer.name}! Logged in as member.")
    elif choice == "3":
        customer = wholesale_customer
        print(f"\nHello {customer.name} ({customer.company_name})! Logged in as wholesale user (20% discount applied at checkout).")
    else:
        customer = Customer("Guest", "", user_type="guest")
        print("\nContinuing as guest.")

    customer.create_cart(inventory)

    # main loop
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
            for name, item in inventory.items.items():
                stock = inventory.storage[name]
                print(f"{item.name} - ${item.price} (in stock: {stock})")

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
                print(f"{item_name} not found. Check the spelling.")

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
                print(f"{item_name} not found.")

        elif action == "5":
            if not customer.cart.storage:
                print("Your cart is empty.")
            else:
                print("\nYour cart:")
                for item_name, qty in customer.cart.storage.items():
                    item = customer.cart.items[item_name]
                    print(f"{item.name} - {qty}x ${item.price}")
                print(f"Subtotal: ${customer.cart.total_value()}")
                print("\nShipping options:")
                for provider, fee in Shipping.OPTIONS.items():
                    print(f"  {provider} - ${fee}")

        elif action == "6":
            if not customer.cart.storage:
                print("Your cart is empty.")
                continue

            # Personal details
            print("\nPersonal details:")
            if customer.user_type != "guest" and customer.name and customer.email:
                print(f"Name:    {customer.name}")
                print(f"Email:   {customer.email}")
                print(f"Address: {customer.address}")
                if customer.user_type == "wholesale" and customer.company_name:
                    print(f"Company: {customer.company_name}")
                personal_details = {"name": customer.name, "email": customer.email, "address": customer.address}
            else:
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                address = input("Address: ").strip()
                personal_details = {"name": name, "email": email, "address": address}

            # Shipping
            print("\nChoose a shipping option:")
            for provider, fee in Shipping.OPTIONS.items():
                print(f"  {provider} - ${fee}")

            shipping_choice = input("Enter UPS or DHL: ").strip().upper()
            if shipping_choice not in Shipping.OPTIONS:
                print("Invalid shipping option. Please enter UPS or DHL.")
                continue
            shipping = Shipping(shipping_choice)

            # Payment
            payment = PaymentMethod.from_input(customer.user_type)
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
