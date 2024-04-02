import sqlite3
import random
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Create Expenses table
cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (
                    id INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    date DATE NOT NULL,
                    account TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES Users(id))''')

# Create Income table
cursor.execute('''CREATE TABLE IF NOT EXISTS Income (
                    id INTEGER PRIMARY KEY,
                    date DATE NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES Users(id))''')

# Function to generate random transactions for Expenses table
def generate_expenses():
    for month in range(1, 13):  # Loop through each month of the year
        for _ in range(1000):  # Generate 1000 entries for each month
            type = random.choice(['expense', 'transfer'])
            date = datetime(2023, month, random.randint(1, 28)).strftime('%Y-%m-%d')
            account = random.choice(['Savings', 'Checking', 'Credit Card'])
            category = random.choice(['Groceries', 'Utilities', 'Entertainment', 'Transportation', 'Dining Out'])
            amount = round(random.uniform(10, 1000), 2)
            description = ' '.join(random.sample(['Random', 'Expense', 'Transaction', 'for', 'User', '1'], random.randint(3, 6)))
            user_id = 1  # Set user_id to 1

            cursor.execute('''INSERT INTO Expenses (type, date, account, category, amount, description, user_id)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', (type, date, account, category, amount, description, user_id))

# Function to generate random transactions for Income table
def generate_income():
    for month in range(1, 13):  # Loop through each month of the year
        for _ in range(1000):  # Generate 1000 entries for each month
            date = datetime(2023, month, random.randint(1, 28)).strftime('%Y-%m-%d')
            category = random.choice(['Salary', 'Freelance', 'Investments', 'Gifts', 'Other'])
            amount = round(random.uniform(1000, 5000), 2)
            description = ' '.join(random.sample(['Random', 'Income', 'Transaction', 'for', 'User', '1'], random.randint(3, 6)))
            user_id = 1  # Set user_id to 1

            cursor.execute('''INSERT INTO Income (date, category, amount, description, user_id)
                              VALUES (?, ?, ?, ?, ?)''', (date, category, amount, description, user_id))

# Generate random transactions for Expenses table
generate_expenses()

# Generate random transactions for Income table
generate_income()

# Commit the changes and close the connection
conn.commit()
conn.close()
