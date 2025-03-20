import sqlite3
import bcrypt

def add_test_user(username, email, password, full_name, company_name=None):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        # Hash the password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        
        # Insert the new user
        c.execute('''
            INSERT INTO users (username, email, password_hash, full_name, company_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, hashed_password.decode('utf-8'), full_name, company_name))
        
        user_id = c.lastrowid
        conn.commit()
        print(f"Added user: {username} with ID: {user_id}")
        return True
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            print(f"Error: Username '{username}' already exists")
        elif "email" in str(e):
            print(f"Error: Email '{email}' already exists")
        else:
            print(f"Error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    # Add a test user
    add_test_user("testuser", "test@example.com", "password123", "Test User", "Test Company")