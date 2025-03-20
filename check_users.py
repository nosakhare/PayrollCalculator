import sqlite3

def check_users():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    # Check users
    c.execute('SELECT id, username, email, password_hash FROM users')
    users = c.fetchall()
    print('Users:')
    for user in users:
        print(user)
    
    # Check employees
    c.execute('SELECT id, user_id, staff_id, full_name FROM employees')
    employees = c.fetchall()
    print('\nEmployees:')
    for employee in employees:
        print(employee)
    
    conn.close()

if __name__ == "__main__":
    check_users()