#==========Class version================

import csv      #csv module to read and write csv files 
import os       #os module to interact with the operating system
import json     #json module to read and write json files
import sys
from datetime import datetime       #datetime module to work with date and time
from typing import List, Dict, Optional     #typing module to define types
from dataclasses import dataclass, asdict       
from collections import defaultdict

@dataclass
class Expense:
    id: int
    description: str
    amount: float
    category: str
    date: str 

class ExpenseTracker:
    def __init__(self, expense_file='expense.json', budget_file='budgets.json'):
        self.expense_file = expense_file
        self.budget_file = budget_file
        self.expenses = self.load_expenses()
        self.budgets = self.load_budgets()
        self.next_id = max([expense.id for expense in self.expenses], default=0) + 1

    def load_expenses(self) -> List[Expense]:
        if os.path.exists(self.expense_file):
            try:
                with open(self.expense_file, 'r') as f:
                    data = json.load(f)
                    return [Expense(**item) for item in data]
            except (FileNotFoundError, json.JSONDecodeError):
                return []
        return []

    def load_budgets(self) -> Dict[str, float]:
        if os.path.exists(self.budget_file):
            try:
                with open(self.budget_file, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
        return {}

    def save_expenses(self):
        with open(self.expense_file, 'w') as f:
            json.dump([asdict(expense) for expense in self.expenses], f, indent=2)
        
    def save_budgets(self):
        with open(self.budget_file, 'w') as f:
            json.dump(self.budgets, f, indent=2)
    


    def add_expense(self, description: str, amount:float, category: str = "other"):
        """Add a new expense"""
        if amount <= 0:
            print("Error: Amount must be positive.")
            return 
        
        expense = Expense(
            id=self.next_id,
            description=description,
            amount=amount,
            category=category,
            date=datetime.now().strftime('%Y-%m-%d')
        )

        self.expenses.append(expense)
        self.next_id += 1
        self.save_expenses()

        self.check_budget(expense.date[:7])

        print(f"Expense added successfully! (ID: {expense.id})")
        print(f"Description: {expense.description}, Amount: {expense.amount}, Category: {expense.category}, Date: {expense.date}")

    
    def update_expense(self, expense_id:int, **kwargs):
        for expense in self.expenses:
            if expense.id == expense_id:
                for key, value in kwargs.items():
                    if hasattr(expense, key):
                        setattr(expense, key, value)
                self.save_expenses()
                print(f"Expense updated successfully! (ID: {expense_id})")
                return

        print(f"Error: Expense with ID {expense_id} not found.")

    def delete_expenses(self, expense_id: int):
        for i, expense in enumerate(self.expenses):
            if expense.id == expense_id:
                self.expenses.pop(i)
                self.save_expenses()
                print(f"Expense deleted successfully! (ID: {expense_id})")
                return

        print(f"Error: Expense with ID {expense_id} not found.")

    def view_all_expenses(self, filter_category: Optional[str] = None):
        if not self.expenses:      
            print("No expenses found.")
            return
        
        filtered_expenses = self.expenses       # If no filter is provided, show all expenses
        if filter_category:     # Filter expenses by category
            filtered_expenses = [e for e in self.expenses if e.category.lower() == filter_category.lower()]
            if not filtered_expenses:
                print(f"No expenses found for category: {filter_category}")
                return
            
        print("\n" + "=" * 60)
        print(f"{'ID':<5} {'Date':<12} {'Category':<15} {'Description':<25} {'Amount':<10}")
        print("-"*60)

        total = 0
        for expense in filtered_expenses:
            print(f"{expense.id:<5} {expense.date:<12} {expense.category:<15} {expense.description[:23]:<25} {expense.amount:<10.2f}")
            total += expense.amount

        print("-"*60)
        print(f"{'Total:':<57} Rs.{total:<10.2f}")
        print("=" * 60)

    def view_summary(self, month: Optional[str] = None):
        if not self.expenses:
            print("No expenses found.")
            return
        
        filtered_expenses = self.expenses
        if month:
            if len(month) == 7 and month[4] == '-':
                filtered_expenses = [e for e in self.expenses if e.date.startswith(month)]
            else:
                print("Error: Month format should be YYYY-MM")
                return
        
        if not filtered_expenses:
            print(f"No expenses found for {month if month else 'any month'}.")
            return
        
        #Calculate totals by category
        category_totals = defaultdict(float)
        monthly_total = 0

        for expense in filtered_expenses:
            category_totals[expense.category] += expense.amount
            monthly_total += expense.amount
        
        month_str = f"for {month}" if month else "Overall"
        print(f"\n{'='*40}")
        print(f"EXPENSE SUMMARY {month_str}")
        print(f"{'='*40}")

        for category, total in sorted(category_totals.items()):
            percentage = (total / monthly_total * 100) if monthly_total > 0 else 0
            print(f"{category:<20} Rs.{total:>10.2f} ({percentage:>5.1f}%)")

        print(f"{'-'*40}")
        print(f"{'TOTAL':<20} Rs.{monthly_total:>10.2f}")

        #Check budget if viewing monthly summary
        if month:
            self.check_budget(month, monthly_total)

    def check_budget(self, month: str, total_spent: Optional[float] = None):
        """Check if budget is exceeded for a given month."""
        if month in self.budgets:
            budget = self.budgets[month]
            if total_spent is None:
                total_spent = sum(expense.amount for expense in self.expenses if expense.date.startswith(month))
            
            if total_spent > budget:
                print(f"\n⚠️ Budget for {month} exceeded! Total spent: Rs.{total_spent:.2f}, Budget: Rs.{budget:.2f}")
                print(f"   Over Budget by: Rs. {total_spent - budget:.2f}")
            elif total_spent > budget * 0.9:
                print(f"\n⚠️ Budget for {month} approaching! Total spent: Rs.{total_spent:.2f}, Budget: Rs.{budget:.2f}")
                print(f"   Remaining Budget by: Rs. {total_spent - budget:.2f}")


    def set_budget(self, month: str, amount: float):
        """Set budget for a  specific month."""
        if amount < 0:
            print("Error: Budget amount cannot be negative.")
            return

        self.budgets[month] = amount
        self.save_budgets()
        print(f"Budget for {month} set to Rs.{amount:.2f}")
        

    def export_to_csv(self, filename: str = "expenses_exp.csv"):
        if not self.expenses:
            print("No expenses found.")
            return

        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['ID', 'Date', 'Category', 'Description', 'Amount']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for expense in self.expenses:
                    writer.writerow({
                        'ID': expense.id,
                        'Date': expense.date,
                        'Category': expense.category,
                        'Description': expense.description,
                        'Amount': expense.amount
                    })

            print(f"Expenses exported to {filename} successfully.")
        except Exception as e:
            print(f"Error exporting to csv: {e}")


    def get_categories(self) -> List[str]:
        return sorted(set(expense.category for expense in self.expenses))


def display_menu():
    """display the main menu."""
    print("\n" + "="*50)
    print("Expense Tracker")
    print("="*50)
    print("1. Add Expense")
    print("2. Update Expense")
    print("3. Delete Expense")
    print("4. View All Expenses")
    print("5. View Summary")
    print("6. View Summary by month")
    print("7. Set Monthly Budget")
    print("8. Export to CSV")
    print("9. View Categories")
    print("0. Exit")
    print("="*50)

def main():
    tracker = ExpenseTracker()

    while True:
        display_menu()

        try:
            choice = input("\Enter your choice (0-9): ").strip()

            if choice == '0':
                print("Goodbye!")
                break

            elif choice == '1':
                print("\n==== Add New Expense ====")
                description = input("Enter description: ").strip()

                try:
                    amount = float(input("Enter the amount: ").strip())
                except ValueError:
                    print("Error: Please enter a valid number for amount.")
                    continue

                category = input("Enter the Category (default: Other): ").strip()
                if not category:
                    category = "Other"

                
                #category  = input("Enter the category: ").strip()
                tracker.add_expense(description, amount, category)

            elif choice == '2':
                print("\n---Update Expenses----")
                try:
                    expense_id = int(input("Enter the expense id to update: ").strip())
                except ValueError:
                    print("Error: Please enter a valid ID number.")
                    continue

                print("Leave field blank to keep current value.")
                description = input("Enter new description: ").strip()
                amount_str = input("Enter new amount: ").strip()
                category = input("Enter new category: ").strip()

                updates = {}
                if description:
                    updates['description'] = description

                if amount_str:
                    try:
                        updates['amount'] = float(amount_str)
                    except ValueError:
                        print("Error: Please enter a valid number for amount.")
                        continue

                if category:
                    updates['category'] = category

                if updates:
                    tracker.update_expense(expense_id, **updates)
                else:
                    print("No changes made.")
            
            elif choice == "3":
                print("\n---Delete Expenses----")
                try:
                    expense_id = int(input("Enter the expense id to delete: ").strip())
                except ValueError:
                    print("Error: Please enter a valid expense id number.")
                    continue

                confirm = input(f"Are you sure you want to delete expense ID {expense_id}? (y/n): ")

                if confirm.lower() == 'y':
                    tracker.delete_expenses(expense_id)

            elif choice == '4':
                print("\n===View All Expenses====")
                filter_by = input("Filter by category (leave blank for all): ").strip()

                if filter_by:
                    tracker.view_all_expenses(filter_category=filter_by)
                else:
                    tracker.view_all_expenses()
            
            elif choice == '5':
                print("\n===View Summary===")
                tracker.view_summary()

            elif choice == '6':
                print("\n===View Summary by Month===")
                month = input("Enter the month (YYYY-MM): ").strip()
                tracker.view_summary(month=month)

            elif choice == '7':
                print("\n===Set Monthly Budget===")
                month = input("Enter the month (YYYY-MM): ").strip()
                try:
                    amount = float(input("Enter the budget amount: ").strip())
                    tracker.set_budget(month, amount)
                except ValueError:
                    print("Error: Please enter a valid number for amount.")
            
            elif choice == '8':
                print("\n===Export to CSV===")
                filename = input("Enter the filename (default: expenses_exp.csv): ").strip()
                if not filename:
                    filename = "expenses_exp.csv"
                tracker.export_to_csv(filename)
                
            elif choice == "9":
                print("\n===View Categories===")
                categories = tracker.get_categories()
                if categories:
                    print("Categories:", ", ".join(categories))
                else:
                    print("No categories found.")

            else:
                print("Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print("\n\Goodbye!")
            break
        except Exception as e:
            print(f"An Error occurred: {e}")
            

if __name__ == "__main__":
    main()