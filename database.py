import sqlite3
import os
from datetime import datetime

def init_db():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    # Create employees table (existing)
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

    # Create payroll_periods table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payroll_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            closed_at TEXT
        )
    ''')

    # Create payroll_runs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS payroll_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_id INTEGER NOT NULL,
            run_date TEXT NOT NULL,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'pending_approval', 'approved', 'rejected')),
            approved_by TEXT,
            approved_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
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
    conn.close()

# Add functions for payroll period management
def create_payroll_period(period_name, start_date, end_date):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO payroll_periods (period_name, start_date, end_date)
            VALUES (?, ?, ?)
        ''', (period_name, start_date, end_date))
        conn.commit()
        return True, "Payroll period created successfully"
    except Exception as e:
        return False, f"Error creating payroll period: {str(e)}"
    finally:
        conn.close()

def get_active_payroll_period():
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM payroll_periods WHERE status = "active" ORDER BY start_date DESC LIMIT 1')
    period = c.fetchone()

    conn.close()
    return dict(period) if period else None

def create_payroll_run(period_id):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        run_date = datetime.now().strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO payroll_runs (period_id, run_date)
            VALUES (?, ?)
        ''', (period_id, run_date))
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

def update_payroll_run_status(run_id, status, approver=None):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        if status == 'approved':
            c.execute('''
                UPDATE payroll_runs 
                SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, approver, run_id))
        else:
            c.execute('''
                UPDATE payroll_runs 
                SET status = ?
                WHERE id = ?
            ''', (status, run_id))
        conn.commit()
        return True, f"Payroll run status updated to {status}"
    except Exception as e:
        return False, f"Error updating payroll run status: {str(e)}"
    finally:
        conn.close()

def get_employee_by_id(employee_id):
    conn = sqlite3.connect('payroll.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
    employee = c.fetchone()

    conn.close()
    return dict(employee) if employee else None

def add_employee(employee_data):
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()

    try:
        # Check if employee exists
        c.execute('SELECT id FROM employees WHERE staff_id = ?', (employee_data['staff_id'],))
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
                WHERE staff_id = ?
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
                employee_data['staff_id']
            ))
            conn.commit()
            return True, "Employee updated successfully"
        else:
            # Insert new employee
            c.execute('''
                INSERT INTO employees (
                    staff_id, email, full_name, department, job_title,
                    annual_gross_pay, start_date, end_date, contract_type,
                    reimbursements, other_deductions, voluntary_pension,
                    rsa_pin, account_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
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