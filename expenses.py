import streamlit as st
import sqlite3
import csv
import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Function to add transaction (expense, income, or transfer)
def add_transaction(user_id):
    st.header("Add Transaction")
    
    # Connect to SQLite database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    type_ = st.selectbox("Type", ["Expense", "Income", "Transfer"])
    date_ = st.date_input("Date")
    account_ = st.selectbox("Account", ["Cash", "Card", "Custom"])
    if account_ == "Custom":
        account_ = st.text_input("Enter Custom Account:")
    category_ = st.text_input("Category")
    amount_ = st.number_input("Amount", step=0.01)
    description_ = st.text_input("Description")

    if st.button("Submit"):
        # Insert transaction into appropriate table in the database
        if type_ == 'Expense' or type_ == 'Transfer':
            cursor.execute('''INSERT INTO Expenses (type, date, account, category, amount, description, user_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', (type_.lower(), date_, account_, category_, amount_, description_, user_id))
            
            # Check if the total expenses for the current month exceed the budget
            month = date_.month
            year = date_.year
            cursor.execute('''SELECT SUM(amount) FROM Expenses WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?''', (user_id, str(month), str(year)))
            total_expenses = cursor.fetchone()[0] or 0
            
            cursor.execute('''SELECT budget FROM Budgets WHERE user_id = ? AND month = ? AND year = ?''', (user_id, month, year))
            monthly_budget = cursor.fetchone()
            
            if monthly_budget is not None:  # Check if budget is set
                budget = monthly_budget[0]
                if total_expenses + amount_ > budget:
                    st.warning("Warning: Total expenses for this month exceed the monthly budget!")
            else:
                st.warning("No monthly budget set. You may consider setting a budget for this month.")

        elif type_ == 'Income':
            cursor.execute('''INSERT INTO Income (date, category, amount, description, user_id)
                            VALUES (?, ?, ?, ?, ?)''', (date_, category_, amount_, description_, user_id))

        conn.commit()
        st.success("Transaction added successfully!")

    # Close the connection
    conn.close()


# Function to get total expenses for a specific month
def get_total_expenses_for_month(month, year, user_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT SUM(amount) FROM Expenses WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ? AND user_id = ?''', (str(month).zfill(2), str(year), user_id))
    total_expenses = cursor.fetchone()[0]
    conn.close()
    return total_expenses

# Function to get budget for a specific month
def get_budget_for_month(month, year, user_id, cursor=None):
    if cursor is None:
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
    
    cursor.execute('''SELECT budget FROM Budgets WHERE month = ? AND year = ? AND user_id = ?''', (month, year, user_id))
    budget = cursor.fetchone()
    
    if cursor is None:
        conn.close()
    
    return budget[0] if budget else 0

    
# Function to view transactions menu
def view_transactions_menu(user_id, cursor):
    st.header("Transactions Menu")
    choice = st.radio("Select an option", ["View Expenses & Income for Current Month", "View Expenses & Income for Specific Month", "Delete Transaction", "Back"])

    if choice == "View Expenses & Income for Current Month":
        view_expenses_and_income_for_current_month(user_id, cursor)
    elif choice == "View Expenses & Income for Specific Month":
        view_expenses_and_income_for_specific_month(user_id, cursor)
    elif choice == "Delete Transaction":
        delete_transaction_menu(user_id, cursor)

# Function to view expenses and income for the current month
def view_expenses_and_income_for_current_month(user_id, cursor):
    st.header("View Expenses & Income for Current Month")
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - datetime.timedelta(days=1)
    
    # Retrieve expenses for the current month
    cursor.execute('''SELECT * FROM Expenses WHERE date BETWEEN ? AND ? AND user_id = ?''', (start_of_month, end_of_month, user_id))
    expenses = cursor.fetchall()
    
    total_expenses = sum(float(expense[5]) for expense in expenses)
    
    st.write("Expenses:")
    if not expenses:
        st.write("No expenses found for the current month.")
    else:
        expense_columns = ["ID", "Type", "Date", "Account", "Category", "Amount", "Description", "User ID"]
        expenses_df = pd.DataFrame(expenses, columns=expense_columns)
        st.table(expenses_df)

    # Retrieve income for the current month
    cursor.execute('''SELECT * FROM Income WHERE date BETWEEN ? AND ? AND user_id = ?''', (start_of_month, end_of_month, user_id))
    income = cursor.fetchall()
    total_income = sum(float(income_entry[3]) for income_entry in income)

    st.write("\nIncome:")
    if not income:
        st.write("No income found for the current month.")
    else:
        income_columns = ["ID", "Date", "Category", "Amount", "Description", "User ID"]
        income_df = pd.DataFrame(income, columns=income_columns)
        st.table(income_df)

    # Calculate remaining balance for the current month
    remaining_balance = total_income - total_expenses
    st.write("\nTotal Expenses for the current month:", total_expenses)
    st.write("Total Income for the current month:", total_income)
    st.write("Remaining Balance for the current month:", remaining_balance)

# Function to view expenses and income for a specific month
def view_expenses_and_income_for_specific_month(user_id, cursor):
    st.header("View Expenses & Income for Specific Month")
    month = st.number_input("Enter month (1-12)", min_value=1, max_value=12)
    year = st.number_input("Enter year (YYYY)", min_value=1900, max_value=9999)

    start_of_month = datetime.date(year, month, 1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - datetime.timedelta(days=1)
    
    # Retrieve expenses for the specific month
    cursor.execute('''SELECT * FROM Expenses WHERE date BETWEEN ? AND ? AND user_id = ?''', (start_of_month, end_of_month, user_id))
    expenses = cursor.fetchall()
    total_expenses = sum(float(expense[5]) for expense in expenses)
    
    st.write("Expenses:")
    if not expenses:
        st.write(f"No expenses found for {start_of_month.strftime('%B %Y')}.")
    else:
        expense_columns = ["ID", "Type", "Date", "Account", "Category", "Amount", "Description", "User ID"]
        expenses_df = pd.DataFrame(expenses, columns=expense_columns)
        st.table(expenses_df.drop(columns=["User ID"]))

    # Retrieve income for the specific month
    cursor.execute('''SELECT * FROM Income WHERE date BETWEEN ? AND ? AND user_id = ?''', (start_of_month, end_of_month, user_id))
    income = cursor.fetchall()
    total_income = sum(float(income_entry[3]) for income_entry in income)

    st.write("\nIncome:")
    if not income:
        st.write(f"No income found for {start_of_month.strftime('%B %Y')}.")
    else:
        income_columns = ["ID", "Date", "Category", "Amount", "Description", "User ID"]
        income_df = pd.DataFrame(income, columns=income_columns)
        st.table(income_df.drop(columns=["User ID"]))

    # Calculate remaining balance for the specific month
    remaining_balance = total_income - total_expenses
    st.write("\nTotal Expenses for the specific month:", total_expenses)
    st.write("Total Income for the specific month:", total_income)
    st.write("Remaining Balance for the specific month:", remaining_balance)

# Function to delete transaction menu
def delete_transaction_menu(user_id, cursor):
    st.header("Delete Transaction Menu")
    choice = st.radio("Select an option", ["Delete Expense by ID", "Delete Income by ID", "Back"])

    if choice == "Delete Expense by ID":
        delete_expense_id = st.number_input("Enter the ID of the expense to delete:", min_value=1, step=1)
        if st.button("Delete Expense"):
            delete_transaction_by_id('expense', user_id, delete_expense_id, cursor)
    elif choice == "Delete Income by ID":
        delete_income_id = st.number_input("Enter the ID of the income to delete:", min_value=1, step=1)
        if st.button("Delete Income"):
            delete_transaction_by_id('income', user_id, delete_income_id, cursor)

# Function to delete expense or income by ID
def delete_transaction_by_id(transaction_type, user_id, transaction_id, cursor):
    st.header(f"Delete {transaction_type.capitalize()} by ID")
    table_name = 'Expenses' if transaction_type == 'expense' else 'Income'

    # Connect to SQLite database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    # Delete transaction
    cursor.execute(f'''DELETE FROM {table_name} WHERE id = ? AND user_id = ?''', (transaction_id, user_id))
    conn.commit()
    st.success(f"{transaction_type.capitalize()} with ID {transaction_id} deleted successfully.")

    # Close the connection
    conn.close()

# Function to set budget for a specific category and month
def set_budget(user_id):
    st.header("Set Budget")
    
    # Connect to SQLite database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    month = st.number_input("Enter month (1-12)", min_value=1, max_value=12)
    year = st.number_input("Enter year (YYYY)", min_value=1900, max_value=9999)
    budget = st.number_input("Enter budget amount", step=0.01)

    submitted = st.button("Submit")
    if submitted:
        # Check if budget entry already exists for the specified category, month, and year
        cursor.execute('''SELECT * FROM Budgets WHERE month = ? AND year = ? AND user_id = ?''', (month, year, user_id))
        existing_budget = cursor.fetchone()

        if existing_budget:
            # Update existing budget entry
            cursor.execute('''UPDATE Budgets SET budget = ? WHERE id = ?''', (budget, existing_budget[0]))
            st.success("Budget updated successfully.")
        else:
            # Insert new budget entry
            cursor.execute('''INSERT INTO Budgets (month, year, budget, user_id) VALUES (?, ?, ?, ?)''', (month, year, budget, user_id))
            st.success("Budget set successfully.")

        conn.commit()
        conn.close()  # Close the connection

# Function to export expenses and income to a CSV file
def export_to_csv(cursor):
    # Connect to SQLite database
    conn = sqlite3.connect('expenses.db')
    
    # Retrieve expenses data
    cursor.execute('''SELECT id, type, date, account, category, amount, description, user_id FROM Expenses''')
    expenses_data = cursor.fetchall()
    
    # Retrieve income data
    cursor.execute('''SELECT id, date, category, amount, description, user_id FROM Income''')
    income_data = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    # Convert fetched data into DataFrames
    expenses_df = pd.DataFrame(expenses_data, columns=['TransactionID', 'Type', 'Date', 'Account', 'Category', 'Amount', 'Description', 'UserID'])
    income_df = pd.DataFrame(income_data, columns=['TransactionID', 'Date', 'Category', 'Amount', 'Description', 'UserID'])
    
    # Concatenate expenses and income DataFrames
    combined_df = pd.concat([expenses_df, income_df], ignore_index=True)
    
    # Export combined DataFrame to a CSV file
    combined_df.to_csv('expenses_and_income.csv', index=False)
    
    st.success("Expenses and income exported to expenses_and_income.csv")

# Call export_to_csv function
if __name__ == "__main__":
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    export_to_csv(cursor)


# Call add_transaction function
if __name__ == "__main__":
    user_id = st.number_input("Enter your user ID:", min_value=1, step=1)
    add_transaction(user_id)
    view_transactions_menu(user_id, cursor)
