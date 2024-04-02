# authentication.py

import streamlit as st
import sqlite3
import re

# Function to create or connect to SQLite database
def connect_database():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    return conn, cursor

# Function to register a new user
def register_user(conn, cursor):
    st.header("Register")
    username = st.text_input("Enter username:")
    password = st.text_input("Enter password:", type="password")
    
    # Password requirements: at least 8 characters, including uppercase, lowercase, digits, and special characters
    if (len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password)
        or not re.search(r"\d", password) or not re.search(r"[!@#$%^&*()-_=+{}\|;:'\",.<>?`~]", password)):
        st.error("Error: Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return

    try:
        cursor.execute('''INSERT INTO Users (username, password) VALUES (?, ?)''', (username, password))
        conn.commit()  # Commit changes to the database
        st.success("User registered successfully!")
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Users.username" in str(e):
            st.error("Error: The username already exists. Please choose a different username.")
        else:
            st.error("Error:", e)


# Function to authenticate an existing user
def authenticate_user(cursor):
    st.header("Login")
    username = st.text_input("Enter username:")
    password = st.text_input("Enter password:", type="password")

    cursor.execute('''SELECT id FROM Users WHERE username = ? AND password = ?''', (username, password))
    user_id = cursor.fetchone()

    if user_id:
        st.success("Login successful!")
        return user_id[0]
    else:
        st.error("Invalid username or password.")
        return None
