import authentication
import expenses
import graphs  # Import graph module

def main():
    authentication.conn = expenses.conn  # Provide database connection to authentication module
    authentication.cursor = expenses.cursor

    while True:
        print("\n\U0001F4B8 Expenses Tracker Menu")
        print("1. Register")
        print("2. Login")
        print("3. Quit")

        choice = input("Enter your choice: ")

        if choice == '1':
            authentication.register_user()
        elif choice == '2':
            user_id = authentication.authenticate_user()
            if user_id:
                while True:
                    print("\n\U0001F4B8 Expenses Tracker Menu")
                    print("1. Add Income & Expenses")
                    print("2. View Income & Expenses")
                    print("3. Export to CSV")
                    print("4. Set Budget for a Specific Month")
                    print("5. View Monthly Pie Chart")
                    print("6. View Yearly Pie Chart")
                    print("7. Quit")

                    choice = input("Enter your choice: ")

                    if choice == '1':
                        expenses.add_transaction(user_id)
                    elif choice == '2':
                        expenses.view_transactions_menu(user_id)
                    elif choice == '3':
                        expenses.export_to_csv()
                    elif choice == '4':
                        expenses.set_budget(user_id)
                    elif choice == '5':
                        view_pie_chart(user_id, 'monthly')
                    elif choice == '6':
                        view_pie_chart(user_id, 'yearly')
                    elif choice == '7':
                        print("Thank you for using Expenses Tracker. Goodbye!")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == '3':
            print("Thank you for using Expenses Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    # Close database connection
    expenses.conn.close()

def view_pie_chart(user_id, chart_type):
    if chart_type == 'monthly':
        print("\n\U0001F4B8 View Monthly Pie Chart")
        month = input("Enter month (1-12): ")
        year = input("Enter year (YYYY): ")
        print("1. Expenses Pie Chart")
        print("2. Income Pie Chart")
        choice = input("Enter your choice: ")
        if choice == '1':
            graphs.view_monthly_expenses(user_id, month, year)
        elif choice == '2':
            graphs.view_monthly_income(user_id, month, year)
        else:
            print("Invalid choice. Please try again.")

    elif chart_type == 'yearly':
        print("\n\U0001F4B8 View Yearly Pie Chart")
        year = input("Enter year (YYYY): ")
        print("1. Expenses Pie Chart")
        print("2. Income Pie Chart")
        choice = input("Enter your choice: ")
        if choice == '1':
            graphs.view_yearly_expenses(user_id, year)
        elif choice == '2':
            graphs.view_yearly_income(user_id, year)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
