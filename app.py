import streamlit as st
from authentication import authenticate_user, register_user
from expenses import add_transaction, view_transactions_menu, export_to_csv, set_budget
import sqlite3
import datetime
import matplotlib.pyplot as plt
import calendar

# Function to create database tables if they don't exist
def create_tables_if_not_exist(conn, cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

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

    cursor.execute('''CREATE TABLE IF NOT EXISTS Income (
                        id INTEGER PRIMARY KEY,
                        date DATE NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES Users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Budgets (
                        id INTEGER PRIMARY KEY,
                        month INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        budget REAL NOT NULL,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES Users(id))''')


# Function to view monthly income and expenses pie charts
def view_monthly_income_expenses_pie_charts(user_id, month, year, cursor):
    st.header(f"Monthly Income and Expenses - {datetime.date(year, month, 1).strftime('%B %Y')}")

    start_of_month = datetime.date(year, month, 1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - datetime.timedelta(days=1)

    cursor.execute('''SELECT category, SUM(amount) FROM Expenses WHERE date BETWEEN ? AND ? AND user_id = ? GROUP BY category''',
                   (start_of_month, end_of_month, user_id))
    expenses_data = cursor.fetchall()

    cursor.execute('''SELECT category, SUM(amount) FROM Income WHERE date BETWEEN ? AND ? AND user_id = ? GROUP BY category''',
                   (start_of_month, end_of_month, user_id))
    income_data = cursor.fetchall()

    if not expenses_data and not income_data:
        st.warning(f"No transactions found for {start_of_month.strftime('%B %Y')}.")
        return

    expenses_categories = [row[0] for row in expenses_data]
    expenses_amounts = [row[1] for row in expenses_data]

    income_categories = [row[0] for row in income_data]
    income_amounts = [row[1] for row in income_data]

    # Plot monthly pie charts using Matplotlib
    fig, axes = plt.subplots(1, 2)
    axes[0].pie(expenses_amounts, labels=expenses_categories, autopct='%1.1f%%', startangle=140)
    axes[0].set_title("Monthly Expenses")

    axes[1].pie(income_amounts, labels=income_categories, autopct='%1.1f%%', startangle=140)
    axes[1].set_title("Monthly Income")

    st.pyplot(fig)

# Function to view yearly income and expenses pie charts
def view_yearly_income_expenses_pie_charts(user_id, year, cursor):
    st.header(f"Yearly Income and Expenses - {year}")

    start_of_year = datetime.date(year, 1, 1)
    end_of_year = datetime.date(year, 12, 31)

    cursor.execute('''SELECT category, SUM(amount) FROM Expenses WHERE date BETWEEN ? AND ? AND user_id = ? GROUP BY category''',
                   (start_of_year, end_of_year, user_id))
    expenses_data = cursor.fetchall()

    cursor.execute('''SELECT category, SUM(amount) FROM Income WHERE date BETWEEN ? AND ? AND user_id = ? GROUP BY category''',
                   (start_of_year, end_of_year, user_id))
    income_data = cursor.fetchall()

    if not expenses_data and not income_data:
        st.warning(f"No transactions found for the year {year}.")
        return

    expenses_categories = [row[0] for row in expenses_data]
    expenses_amounts = [row[1] for row in expenses_data]

    income_categories = [row[0] for row in income_data]
    income_amounts = [row[1] for row in income_data]

    # Plot yearly pie charts using Matplotlib
    fig, axes = plt.subplots(1, 2)
    axes[0].pie(expenses_amounts, labels=expenses_categories, autopct='%1.1f%%', startangle=140)
    axes[0].set_title("Yearly Expenses")

    axes[1].pie(income_amounts, labels=income_categories, autopct='%1.1f%%', startangle=140)
    axes[1].set_title("Yearly Income")

    st.pyplot(fig)

# Function to view yearly bar chart with two bars side by side for each month
def view_yearly_bar_chart(user_id, year, cursor):
    st.header(f"Yearly Bar Chart - {year}")

    months = range(1, 13)
    income = []
    expenses = []

    month_names = [calendar.month_abbr[i] for i in months]  # Get month names

    for month in months:
        start_of_month = datetime.date(year, month, 1)
        end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - datetime.timedelta(days=1)

        cursor.execute('''SELECT SUM(amount) FROM Expenses WHERE date BETWEEN ? AND ? AND user_id = ?''',
                       (start_of_month, end_of_month, user_id))
        expense_total = cursor.fetchone()[0] or 0
        expenses.append(expense_total)

        cursor.execute('''SELECT SUM(amount) FROM Income WHERE date BETWEEN ? AND ? AND user_id = ?''',
                       (start_of_month, end_of_month, user_id))
        income_total = cursor.fetchone()[0] or 0
        income.append(income_total)

    # Define custom colors
    income_color = 'blue'
    expense_color = 'red'  # Dark red color

    # Plot yearly bar chart with two bars side by side for each month
    fig, ax = plt.subplots(figsize=(12, 6)) # Set the figure size to (12, 6) inches
    width = 0.35  # Width of each bar
    x = range(len(months))

    ax.bar([i - width/2 for i in x], income, width, color=income_color, label='Income')
    ax.bar([i + width/2 for i in x], expenses, width, color=expense_color, label='Expenses', alpha=0.5)
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.set_title(f'Yearly Income and Expenses for Year {year}')
    ax.set_xticks(x)
    ax.set_xticklabels(month_names)
    ax.legend()
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    st.pyplot(fig)


def main():
    st.title("Expenses Tracker - By Atharva")

    # Connect to SQLite database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # Create tables if they don't exist
    create_tables_if_not_exist(conn, cursor)

    menu_options = ["Register", "Login", "Quit"]
    choice = st.sidebar.selectbox("Menu", menu_options)

    if choice == "Quit":
        quit_confirmation = st.sidebar.radio("Are you sure you want to quit?", ("Yes", "No"))
        if quit_confirmation == "Yes":
            st.write("Thank you for using the Expenses Tracker!")
            conn.close()
            st.stop()  # Stop the Streamlit app
        else:
            conn.close()
            return

    if choice == "Register":
        register_user(conn, cursor)
    elif choice == "Login":
        user_id = authenticate_user(cursor)
        if user_id:
            user_menu(user_id, cursor)


def user_menu(user_id, cursor):
    st.write(f"Welcome, User {user_id}!")

    st.sidebar.subheader("Menu")
    menu_options = ["Add Transaction", "View Transactions", "Export to CSV", "Set Budget", "View Graphs", "Quit"]
    choice = st.sidebar.selectbox("Select Option", menu_options)

    if choice == "Add Transaction":
        add_transaction(user_id)
    elif choice == "View Transactions":
        view_transactions_menu(user_id, cursor)
    elif choice == "Export to CSV":
        export_to_csv(cursor)
    elif choice == "Set Budget":
        set_budget(user_id)
    elif choice == "View Graphs":
        view_graphs_menu(user_id, cursor)
    elif choice == "Quit":
        confirm_quit = st.sidebar.radio("Are you sure you want to quit?", ("Yes", "No"))
        if confirm_quit == "Yes":
            st.write("Thanks for using the Expenses Tracker!")
            st.stop()  # Stop the app


def view_graphs_menu(user_id, cursor):
    st.subheader("View Graphs")

    graph_options = ["View Pie Chart Monthly", "View Yearly Pie Chart", "View Bar Chart Yearly"]
    graph_choice = st.selectbox("Select Graph", graph_options)

    if graph_choice == "View Pie Chart Monthly":
        month = st.number_input("Enter month (1-12)", min_value=1, max_value=12)
        year = st.number_input("Enter year (YYYY)", min_value=1900, max_value=9999)
        submitted = st.button("Submit")
        if submitted:
            view_monthly_income_expenses_pie_charts(user_id, month, year, cursor)
    elif graph_choice == "View Yearly Pie Chart":
        year = st.number_input("Enter year (YYYY)", min_value=1900, max_value=9999)
        submitted = st.button("Submit")
        if submitted:
            view_yearly_income_expenses_pie_charts(user_id, year, cursor)
    elif graph_choice == "View Bar Chart Yearly":
        year = st.number_input("Enter year (YYYY)", min_value=1900, max_value=9999)
        submitted = st.button("Submit")
        if submitted:
            view_yearly_bar_chart(user_id, year, cursor)

if __name__ == "__main__":
    main()
