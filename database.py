import sqlite3
import os
import bcrypt
from datetime import datetime

def init_db():
    # First, check if we need to run the migration
    db_exists = os.path.exists('payroll.db')
    
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    # Check if migration is needed (if tables exist but don't have user_id column)
    needs_migration = False
    
    if db_exists:
        try:
            # Check if employees table exists without user_id column
            c.execute("PRAGMA table_info(employees)")
            columns = [column[1] for column in c.fetchall()]
            
            if "employees" in [table[0] for table in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                if "user_id" not in columns:
                    needs_migration = True
        except:
            pass
    
    # If migration is needed, run it from the migration script
    if needs_migration:
        conn.close()
        from migrate_db import migrate_database
        migrate_database()
        return
    
    # Otherwise, create the tables normally
    try:
        # Create users table for authentication
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                company_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create employees table with user_id foreign key
        c.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                staff_id TEXT NOT NULL,
                email TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                job_title TEXT NOT NULL,
                annual_gross_pay REAL NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                contract_type TEXT NOT NULL,
                reimbursements REAL DEFAULT 0,
                other_deductions REAL DEFAULT 0,
                voluntary_pension REAL DEFAULT 0,
                rsa_pin TEXT,
                account_number TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (user_id, staff_id),
                UNIQUE (user_id, email)
            )
        ''')

        # Create payroll_periods table with user_id
        c.execute('''
            CREATE TABLE IF NOT EXISTS payroll_periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                period_name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (user_id, period_name)
            )
        ''')

        # Create payroll_runs table with user_id
        c.execute('''
            CREATE TABLE IF NOT EXISTS payroll_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                period_id INTEGER NOT NULL,
                run_date TEXT NOT NULL,
                status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'pending_approval', 'approved', 'rejected')),
                approved_by TEXT,
                approved_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (period_id) REFERENCES payroll_periods (id)
            )
        ''')

        # Create payroll_details table
        c.execute('''
            CREATE TABLE IF NOT EXISTS payroll_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                gross_pay REAL NOT NULL,
                net_pay REAL NOT NULL,
                basic_salary REAL NOT NULL,
                housing REAL NOT NULL,
                transport REAL NOT NULL,
                utility REAL NOT NULL,
                meal REAL NOT NULL,
                clothing REAL NOT NULL,
                pension_employee REAL NOT NULL,
                pension_employer REAL NOT NULL,
                pension_voluntary REAL NOT NULL,
                paye_tax REAL NOT NULL,
                other_deductions REAL NOT NULL,
                reimbursements REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES payroll_runs (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        conn.commit()
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
    finally:
        conn.close()

# Add functions for payroll period management
def create_payroll_period(user_id, period_name, start_date, end_date):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO payroll_periods (user_id, period_name, start_date, end_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, period_name, start_date, end_date))
        conn.commit()
        return True, "Payroll period created successfully"
    except Exception as e:
        return False, f"Error creating payroll period: {str(e)}"
    finally:
        conn.close()

def get_active_payroll_period(user_id):
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM payroll_periods WHERE user_id = ? AND status = "active" ORDER BY start_date DESC LIMIT 1', 
              (user_id,))
    period = c.fetchone()

    conn.close()
    return dict(period) if period else None

def create_payroll_run(user_id, period_id):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        run_date = datetime.now().strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO payroll_runs (user_id, period_id, run_date)
            VALUES (?, ?, ?)
        ''', (user_id, period_id, run_date))
        run_id = c.lastrowid
        conn.commit()
        return True, run_id
    except Exception as e:
        return False, f"Error creating payroll run: {str(e)}"
    finally:
        conn.close()

def save_payroll_details(run_id, employee_details):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO payroll_details (
                run_id, employee_id, gross_pay, net_pay,
                basic_salary, housing, transport, utility,
                meal, clothing, pension_employee, pension_employer,
                pension_voluntary, paye_tax, other_deductions, reimbursements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id, employee_details['employee_id'],
            employee_details['gross_pay'], employee_details['net_pay'],
            employee_details['basic_salary'], employee_details['housing'],
            employee_details['transport'], employee_details['utility'],
            employee_details['meal'], employee_details['clothing'],
            employee_details['pension_employee'], employee_details['pension_employer'],
            employee_details['pension_voluntary'], employee_details['paye_tax'],
            employee_details['other_deductions'], employee_details['reimbursements']
        ))
        conn.commit()
        return True, "Payroll details saved successfully"
    except Exception as e:
        return False, f"Error saving payroll details: {str(e)}"
    finally:
        conn.close()

def update_payroll_run_status(run_id, status, user_id, approver=None):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        # First verify that this run belongs to the user
        c.execute('SELECT id FROM payroll_runs WHERE id = ? AND user_id = ?', (run_id, user_id))
        run = c.fetchone()
        
        if not run:
            return False, "Payroll run not found or you don't have permission to update it"
            
        if status == 'approved':
            c.execute('''
                UPDATE payroll_runs 
                SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (status, approver, run_id, user_id))
        else:
            c.execute('''
                UPDATE payroll_runs 
                SET status = ?
                WHERE id = ? AND user_id = ?
            ''', (status, run_id, user_id))
        conn.commit()
        return True, f"Payroll run status updated to {status}"
    except Exception as e:
        return False, f"Error updating payroll run status: {str(e)}"
    finally:
        conn.close()

def get_employee_by_id(employee_id, user_id):
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM employees WHERE id = ? AND user_id = ?', (employee_id, user_id))
    employee = c.fetchone()

    conn.close()
    return dict(employee) if employee else None

def add_employee(employee_data, user_id):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        # Check if employee exists for this user
        c.execute('SELECT id FROM employees WHERE staff_id = ? AND user_id = ?', 
                  (employee_data['staff_id'], user_id))
        existing_employee = c.fetchone()

        if existing_employee:
            # Update existing employee
            c.execute('''
                UPDATE employees SET
                    email = ?,
                    full_name = ?,
                    department = ?,
                    job_title = ?,
                    annual_gross_pay = ?,
                    start_date = ?,
                    end_date = ?,
                    contract_type = ?,
                    reimbursements = ?,
                    other_deductions = ?,
                    voluntary_pension = ?,
                    rsa_pin = ?,
                    account_number = ?
                WHERE staff_id = ? AND user_id = ?
            ''', (
                employee_data['email'],
                employee_data['full_name'],
                employee_data['department'],
                employee_data['job_title'],
                employee_data['annual_gross_pay'],
                employee_data['start_date'],
                employee_data.get('end_date'),
                employee_data['contract_type'],
                employee_data.get('reimbursements', 0),
                employee_data.get('other_deductions', 0),
                employee_data.get('voluntary_pension', 0),
                employee_data.get('rsa_pin'),
                employee_data['account_number'],
                employee_data['staff_id'],
                user_id
            ))
            conn.commit()
            return True, "Employee updated successfully"
        else:
            # Insert new employee
            c.execute('''
                INSERT INTO employees (
                    user_id, staff_id, email, full_name, department, job_title,
                    annual_gross_pay, start_date, end_date, contract_type,
                    reimbursements, other_deductions, voluntary_pension,
                    rsa_pin, account_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                employee_data['staff_id'],
                employee_data['email'],
                employee_data['full_name'],
                employee_data['department'],
                employee_data['job_title'],
                employee_data['annual_gross_pay'],
                employee_data['start_date'],
                employee_data.get('end_date'),
                employee_data['contract_type'],
                employee_data.get('reimbursements', 0),
                employee_data.get('other_deductions', 0),
                employee_data.get('voluntary_pension', 0),
                employee_data.get('rsa_pin'),
                employee_data['account_number']
            ))
            conn.commit()
            return True, "Employee added successfully"

    except sqlite3.IntegrityError as e:
        if "staff_id" in str(e):
            return False, f"Error: Duplicate staff ID found"
        elif "email" in str(e):
            return False, f"Error: Email address already exists"
        return False, f"Error: Duplicate entry found"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_all_employees(user_id):
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM employees WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    employees = [dict(row) for row in c.fetchall()]

    conn.close()
    return employees

def generate_staff_id(user_id):
    """Generate a unique staff ID"""
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    # Get current year
    year = datetime.now().year % 100

    # Get the latest staff ID for this year for this user
    c.execute("SELECT staff_id FROM employees WHERE user_id = ? AND staff_id LIKE ? ORDER BY staff_id DESC LIMIT 1", 
              (user_id, f'EMP{year}%'))
    result = c.fetchone()

    if result:
        last_id = int(result[0][5:])  # Extract number after EMP{year}
        new_id = last_id + 1
    else:
        new_id = 1

    conn.close()
    return f'EMP{year}{new_id:04d}'  # Format: EMP230001

# Add this function after get_all_employees()

def delete_employee(employee_id, user_id):
    """Delete an employee from the database"""
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    print(f"DEBUG: Attempting to delete employee_id={employee_id} for user_id={user_id}")

    try:
        # First check if employee exists and belongs to the user
        c.execute('SELECT id, staff_id, full_name, user_id FROM employees WHERE id = ?', (employee_id,))
        employee = c.fetchone()
        
        if not employee:
            print(f"DEBUG: Employee with ID {employee_id} not found")
            return False, "Employee not found"
            
        print(f"DEBUG: Found employee: {employee}")
        
        # Check if the employee belongs to this user
        if employee and employee[3] != user_id:
            print(f"DEBUG: Permission denied. Employee has user_id={employee[3]}, but requester has user_id={user_id}")
            return False, "You don't have permission to delete this employee"

        # Delete the employee (ensure to check user_id to maintain data isolation)
        print(f"DEBUG: Executing DELETE query for employee_id={employee_id} and user_id={user_id}")
        c.execute('DELETE FROM employees WHERE id = ? AND user_id = ?', (employee_id, user_id))
        
        if c.rowcount == 0:
            print(f"DEBUG: No rows affected by the DELETE query")
            return False, "No rows were deleted. Possible permission issue."
            
        print(f"DEBUG: Successfully deleted {c.rowcount} rows")
        conn.commit()
        return True, "Employee deleted successfully"
    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        return False, f"Error deleting employee: {str(e)}"
    finally:
        conn.close()

# User Authentication Functions
def register_user(username, email, password, full_name, company_name=None):
    """Register a new user"""
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
        return True, user_id
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists"
        elif "email" in str(e):
            return False, "Email already exists"
        return False, f"Registration error: {str(e)}"
    except Exception as e:
        return False, f"Registration error: {str(e)}"
    finally:
        conn.close()

def login_user(username, password):
    """Authenticate a user"""
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        
        if not user:
            return False, "Invalid username or password"
        
        # Verify password
        stored_password = user['password_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return True, dict(user)
        else:
            return False, "Invalid username or password"
    except Exception as e:
        return False, f"Login error: {str(e)}"
    finally:
        conn.close()

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute('SELECT id, username, email, full_name, company_name, created_at FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None
    finally:
        conn.close()