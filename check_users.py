import sqlite3

def check_users():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        # Get all users
        c.execute('SELECT id, username, email, full_name, company_name FROM users')
        users = c.fetchall()
        
        if not users:
            print("No users found in the database.")
            return
        
        print("\n=== Users in Database ===")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Name: {user[3]}, Company: {user[4]}")
        
        # Check employees count per user
        print("\n=== Employee Count by User ===")
        c.execute('''
            SELECT user_id, COUNT(*) as employee_count
            FROM employees
            GROUP BY user_id
        ''')
        employee_counts = c.fetchall()
        
        if not employee_counts:
            print("No employees found in the database.")
        else:
            for count in employee_counts:
                print(f"User ID: {count[0]}, Employee Count: {count[1]}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()