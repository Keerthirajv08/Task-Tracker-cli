import sys
import os
import json
from datetime import datetime

total = 0

EXPENSE_FILE = "expense_tracker.json"

def load_expenses():
    if not os.path.exists(EXPENSE_FILE):    #if the file does not exist
        return []
    try:
        with open(EXPENSE_FILE, 'r') as f:      #open the file
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_expenses(expenses):
    with open(EXPENSE_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

#program starts from here 

#Add expense
def add_expense(description, amount):
    try:
        amount = float(amount)
        if amount <= 0:
            print("Amount cannot be zero or negative")
            return False
    except ValueError:
        print("amount value must be an integer.")
        return False

    expenses = load_expenses()

    expense_id = 1 if not expenses else max(expense['id'] for expense in expenses) + 1

    #for expense in expenses:
        #expense_id = max(expense_id [for exp_id in expenses]) + 1
    expense = {
        'id': expense_id,
        'description': description,
        'amount': amount,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    #global total
    #total += amount
    expenses.append(expense)
    save_expenses(expenses)

    print(f"Added expense: {description} - {amount}")  
    return True


def update_expense(expense_id, new_description, new_amount):
    expenses = load_expenses()

    try:
        expense_id = int(expense_id)
        #return True
    except ValueError:
        print("Value must be an integer")
        return False
    
    #Validate amount
    try:
        new_amount = float(new_amount)
        if new_amount <= 0:
            print("Amount must be positive")
            return False
    except ValueError:
        print("Amount must be a valid number.")
        return False

    for expense in expenses:
        if expense['id'] == expense_id:
            expense['description'] = new_description
            expense['amount'] = new_amount
            expense['date'] = datetime.now().strftime('%Y-%m-%d')

            save_expenses(expenses)
            print(f"Expense updated:expense_id -{expense['id']} , {expense['description']}")
    return True         

def delete_expense(expense_id):   
    expenses = load_expenses()

    for i ,expense in expenses:
        if expense['id'] == expense_id:
            deleted_exp = expenses.pop(i)
            save_expenses(expenses)

        print(f"Expense deleted - {deleted_exp['description']}")
        return True
    
    print("Expense not found.")
    return False

def list_expenses():
    expenses = load_expenses()

    for expense in expenses:
        print(f"Expense ID: {expense['id']}, Description: {expense['description']}, Amount: {expense['amount']}, Date: {expense['date']}")
    return True

def summary_of_all_exp():
    expenses = load_expenses()

    for expense in expenses:
        global total
        total += expense['amount']
    print(f"Total money spent on all expenses {list_expenses()} is - Rs. {total}")
    #print(f"Money spent on items {expenses['description']}")


def month_summary():
    expenses = load_expenses()

    pass


def show_help():
    print("Usage:")
    print("python expense_tracker.py add \"description\" \"amount\"")
    print("python expense_tracker.py update \"expense_id\" \"new_description\" \"new_amount\"")
    print("python expense_tracker.py delete \"expense_id\"")
    print("python expense_tracker.py list")
    print("python expense_tracker.py summary")
    print("python expense_tracker.py month")
    print("python expense_tracker.py help")

def main():
    if len(sys.argv) < 2:
        show_help()
        return 
    
    command = sys.argv[1].lower()

    try:
        if command == "add":
            if len(sys.argv) < 4:
                print("Description and amount are required.")
                print("Usage: python expense_tracker.py add \"description\" \"amount\" ")
                return
                
            description = sys.argv[2:]
            amount = sys.argv[3]
            add_expense(description, amount)

        elif command == "update":
            if len(sys.argv) < 5:
                print("Expense ID, new description and amount are required.")
                print("Usage: python expense_tracker.py update \"expense_id\" \"new_description\" \"new_amount\"")
                return

            expense_id = sys.argv[2]
            new_description = sys.argv[3:]
            new_amount = sys.argv[4]
            update_expense(expense_id, new_description, new_amount)
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("Expense ID is required.")
                print("Usage: python expense_tracker.py delete \"expense_id\"")
                return

            expense_id = sys.argv[2]
            delete_expense(expense_id)

        elif command == "list":
            list_expenses()
        elif command == "summary":
            summary_of_all_exp()
        elif command == "month":
            month_summary()
        elif command == "help":
            show_help()
        else:
            print("Invalid command.")
            show_help()

    except FileNotFoundError:
        print("Expense file not found.")
        return False
    

if __name__ == "__main__":
    main()




