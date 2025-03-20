import streamlit as st
import sqlite3

def init_debug():
    """Check the current session state and database values"""
    
    st.title("Debug Session State")
    
    st.write("### Current Session State")
    for key in st.session_state:
        st.write(f"**{key}**: {st.session_state[key]}")
    
    st.write("### Database Check")
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Check users
    st.write("#### Users in the Database")
    c.execute('SELECT id, username, email, full_name, company_name FROM users')
    users = c.fetchall()
    for user in users:
        st.write(f"User ID: {user['id']}, Username: {user['username']}, Name: {user['full_name']}")
    
    # Check employees
    st.write("#### Employees in the Database")
    c.execute('SELECT id, user_id, staff_id, full_name, department FROM employees')
    employees = c.fetchall()
    for emp in employees:
        st.write(f"Employee ID: {emp['id']}, User ID: {emp['user_id']}, Staff ID: {emp['staff_id']}, Name: {emp['full_name']}")
    
    conn.close()

# Run the debug function when this script is executed
if __name__ == "__main__":
    init_debug()