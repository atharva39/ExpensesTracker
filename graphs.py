import streamlit as st
import sqlite3
import datetime
import matplotlib.pyplot as plt
from graphs import view_monthly_expenses, view_yearly_expenses, view_monthly_income, view_yearly_income

# Connect to SQLite database
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Function to display pie charts for expenses and income side by side
def view_pie_charts(user_id):
    st.header("View Income and Expenses Pie Charts")

    # Sidebar for selecting options
    option = st.sidebar.radio("Select an option", ["Monthly", "Yearly"])

    # Get current date
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    # Display pie charts based on user selection
    if option == "Monthly":
        st.subheader("Monthly Pie Charts")
        st.write("View Monthly Expenses Pie Chart")
        month_expenses = st.sidebar.number_input("Enter month (1-12)", min_value=1, max_value=12, value=current_month)
        year_expenses = st.sidebar.number_input("Enter year (YYYY)", min_value=1900, max_value=current_year, value=current_year)
        view_monthly_expenses(user_id, month_expenses, year_expenses)

        st.write("View Monthly Income Pie Chart")
        month_income = st.sidebar.number_input("Enter month (1-12)", min_value=1, max_value=12, value=current_month)
        year_income = st.sidebar.number_input("Enter year (YYYY)", min_value=1900, max_value=current_year, value=current_year)
        view_monthly_income(user_id, month_income, year_income)
    elif option == "Yearly":
        st.subheader("Yearly Pie Charts")
        st.write("View Yearly Expenses Pie Chart")
        year_expenses = st.sidebar.number_input("Enter year (YYYY)", min_value=1900, max_value=current_year, value=current_year)
        view_yearly_expenses(user_id, year_expenses)

        st.write("View Yearly Income Pie Chart")
        year_income = st.sidebar.number_input("Enter year (YYYY)", min_value=1900, max_value=current_year, value=current_year)
        view_yearly_income(user_id, year_income)

# Call the function to display the pie charts
if __name__ == "__main__":
    user_id = st.number_input("Enter your user ID:", min_value=1, step=1)
    view_pie_charts(user_id)
