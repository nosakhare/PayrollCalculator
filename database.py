import sqlite3
import os
from datetime import datetime

def init_db():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    # Create employees table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_employee(employee_data):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO employees (
                staff_id, email, full_name, department, job_title,
                annual_gross_pay, start_date, end_date, contract_type,
                reimbursements, other_deductions, voluntary_pension,
                rsa_pin, account_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            employee_data['staff_id'], employee_data['email'],
            employee_data['full_name'], employee_data['department'],
            employee_data['job_title'], employee_data['annual_gross_pay'],
            employee_data['start_date'], employee_data.get('end_date'),
            employee_data['contract_type'], employee_data.get('reimbursements', 0),
            employee_data.get('other_deductions', 0),
            employee_data.get('voluntary_pension', 0),
            employee_data.get('rsa_pin'), employee_data['account_number']
        ))
        conn.commit()
        return True, "Employee added successfully"
    except sqlite3.IntegrityError as e:
        return False, f"Error: Duplicate entry found for staff ID or email"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_all_employees():
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM employees ORDER BY created_at DESC')
    employees = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return employees

def generate_staff_id():
    """Generate a unique staff ID"""
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    # Get current year
    year = datetime.now().year % 100
    
    # Get the latest staff ID for this year
    c.execute("SELECT staff_id FROM employees WHERE staff_id LIKE ? ORDER BY staff_id DESC LIMIT 1", (f'EMP{year}%',))
    result = c.fetchone()
    
    if result:
        last_id = int(result[0][5:])  # Extract number after EMP{year}
        new_id = last_id + 1
    else:
        new_id = 1
    
    conn.close()
    return f'EMP{year}{new_id:04d}'  # Format: EMP230001
