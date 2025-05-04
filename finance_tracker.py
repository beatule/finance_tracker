import csv
import os
from abc import ABC, abstractmethod

class LimitExceededError(Exception):
    pass

class User:
    def __init__(self, name: str, limit: float):
        self.name = name
        self.limit = limit
        self.expenses = []

    def add_expense(self, expense):
        if isinstance(expense, GroupExpense):
            share = expense.get_user_share()
        else:
            share = expense.amount

        if self.total_expenses() + share > self.limit:
            raise LimitExceededError(f"{self.name} has exceeded their spending limit.")

        self.expenses.append(expense)

    def total_expenses(self):
        total = 0
        for e in self.expenses:
            if isinstance(e, GroupExpense):
                total += e.get_user_share()
            else:
                total += e.amount
        return total

    def has_exceeded_limit(self):
        return self.total_expenses() > self.limit


class Expense:
    def __init__(self, amount: float, description: str, user=None):
        self.amount = amount
        self.description = description
        self.user = user  # Added user reference

    def get_details(self):
        return f"{self.description} - €{self.amount}"


class GroupExpense(Expense):
    def __init__(self, amount: float, description: str, users: list):
        super().__init__(amount, description)
        self.users = users

    def get_user_share(self):
        return self.amount / len(self.users)

    def get_details(self):
        user_names = ", ".join([user.name for user in self.users])
        return f"Group ({user_names}): {self.description} - €{self.amount}"


class AbstractExpenseFactory(ABC):
    @abstractmethod
    def create_expense(self, expense_type, amount, description, users=None):
        pass


class ExpenseFactory(AbstractExpenseFactory):
    def create_expense(self, expense_type, amount, description, users=None):
        if expense_type == "personal":
            return Expense(amount, description)
        elif expense_type == "group":
            return GroupExpense(amount, description, users)
        else:
            raise ValueError("Invalid expense type")


class FinanceTracker:
    def __init__(self, users):
        self.expenses = []
        self.users = users
        self.factory = ExpenseFactory()

    def add_expense(self, expense):
        self.expenses.append(expense)

    def print_expenses(self):
        if not self.expenses:
            print("No expenses to show.")
            return
        for e in self.expenses:
            if isinstance(e, GroupExpense):
                print(e.get_details())
            else:
                if e.user:
                    print(f"{e.user.name}'s: {e.get_details()}")
                else:
                    print(f"Personal: {e.get_details()}")

    def save_to_file(self, filename="expenses.csv"):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            for e in self.expenses:
                if isinstance(e, GroupExpense):
                    users = ";".join(user.name for user in e.users)
                    writer.writerow(["GroupExpense", e.amount, e.description, users])
                else:
                    writer.writerow(["Expense", e.amount, e.description, e.user.name])

    def load_from_file(self, filename="expenses.csv"):
        self.expenses.clear()
        if not os.path.exists(filename):
            print(f"No existing file found: {filename}")
            return

        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                expense_type, amount, description, user_field = row
                amount = float(amount)

                if expense_type == "GroupExpense":
                    user_names = user_field.split(";")
                    users = []
                    for name in user_names:
                        user = self.find_user(name)
                        if user:
                            users.append(user)
                    if users:
                        expense = GroupExpense(amount, description, users)
                        self.expenses.append(expense)
                        for u in users:
                            u.add_expense(expense)
                else:  # "Expense" (personal)
                    user = self.find_user(user_field)
                    if user:
                        expense = Expense(amount, description, user)
                        self.expenses.append(expense)
                        user.add_expense(expense)

    def find_user(self, name):
        return next((u for u in self.users if u.name == name), None)


def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def main():
    users = []
    try:
        with open('users.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                name, limit = row
                users.append(User(name, float(limit)))
    except FileNotFoundError:
        print("No existing file found: users.csv")

    tracker = FinanceTracker(users)
    tracker.load_from_file()

    while True:
        print("\nAvailable options:")
        print("1. Add an expense")
        print("2. Change spending limit")
        print("3. Add a new user")
        print("4. Exit")

        choice = input("Choose an option (1, 2, 3, 4): ").strip()

        if choice == '1':
            name = input("Enter your name to add an expense: ").strip()
            user = next((u for u in users if u.name == name), None)
            if not user:
                print(f"User {name} does not exist.")
                continue

            expense_type = input("Enter expense type ('personal' or 'group'): ").strip().lower()
            amount = get_float("Enter amount: ")
            description = input("Enter description: ")

            factory = ExpenseFactory()
            if expense_type == 'group':
                group_user_names = input("Enter comma-separated user names (including yourself): ").strip().split(",")
                group_user_names = [n.strip() for n in group_user_names]
                group_users = [u for u in users if u.name in group_user_names]
                missing = set(group_user_names) - {u.name for u in group_users}
                if missing:
                    print(f"Error: These users do not exist: {', '.join(missing)}")
                    continue
                expense = factory.create_expense("group", amount, description, group_users)
                exceeding_users = []
                for u in group_users:
                    temp_total = u.total_expenses() + expense.get_user_share()
                    if temp_total > u.limit:
                        exceeding_users.append(u.name)
                if exceeding_users:
                    print(f"\u274c These users would exceed their limit: {', '.join(exceeding_users)}")
                else:
                    for u in group_users:
                        u.add_expense(expense)
                    tracker.add_expense(expense)
                    print("Expense added!")
            else:
                try:
                    expense = factory.create_expense("personal", amount, description)
                    expense.user = user
                    user.add_expense(expense)
                    tracker.add_expense(expense)
                    print("Expense added!")
                except LimitExceededError as e:
                    print(f"\u274c {e}")

        elif choice == '2':
            name = input("Enter your name: ").strip()
            user = next((u for u in users if u.name == name), None)
            if user:
                new_limit = get_float(f"Enter new limit for {name}: ")
                user.limit = new_limit
                print(f"{name}'s limit updated to {new_limit}")
            else:
                print(f"User {name} not found.")

        elif choice == '3':
            name = input("Enter new user's name: ").strip()
            if name in [u.name for u in users]:
                print(f"User {name} already exists.")
                continue
            limit = get_float(f"Enter spending limit for {name}: ")
            users.append(User(name, limit))
            print(f"User {name} added successfully.")

        elif choice == '4':
            break

        # Save data after each loop
        with open('users.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for u in users:
                writer.writerow([u.name, u.limit])
        tracker.save_to_file()

    print("\nCurrent Users and Their Spending Limits:")
    for u in users:
        print(f"{u.name}: €{u.limit}")

    print("\nAll Expenses:")
    tracker.print_expenses()


if __name__ == "__main__":
    main()



import unittest
from finance_tracker import User, GroupExpense, Expense, LimitExceededError

class TestFinanceTracker(unittest.TestCase):

    def setUp(self):
        self.user1 = User("Alice", 100)
        self.user2 = User("Bob", 50)

    def test_personal_expense_within_limit(self):
        expense = Expense(30, "Lunch")
        self.user1.add_expense(expense)
        self.assertEqual(self.user1.total_expenses(), 30)

    def test_personal_expense_exceeds_limit(self):
        expense = Expense(150, "Laptop")
        with self.assertRaises(LimitExceededError):
            self.user1.add_expense(expense)

    def test_group_expense_within_limit(self):
        expense = GroupExpense(40, "Dinner", [self.user1, self.user2])
        self.user1.add_expense(expense)
        self.user2.add_expense(expense)
        self.assertAlmostEqual(self.user1.total_expenses(), 20)
        self.assertAlmostEqual(self.user2.total_expenses(), 20)

    def test_group_expense_exceeds_limit(self):
        self.user1 = User("Charlie", 10) 
        expense = GroupExpense(100, "Trip", [self.user1, self.user2])
        with self.assertRaises(LimitExceededError):
            self.user1.add_expense(expense)

if __name__ == '__main__':
    unittest.main()
