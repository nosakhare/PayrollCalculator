import sqlite3
import os

def migrate_database():
    """
    Migrates the existing database to add user_id columns and create necessary tables
    """
    print("Starting database migration...")
    
    # Check if the database file exists
    if not os.path.exists('payroll.db'):
        print("Database file not found. No migration needed.")
        return
    
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    
    # Start a transaction
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # Check if users table exists, if not create it
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
        
        # Create a default admin user if no users exist
        c.execute('SELECT COUNT(*) FROM users')
        user_count = c.fetchone()[0]
        
        if user_count == 0:
            # Generate a hash for the default password "admin"
            # In a real-world app, you'd use bcrypt, but we'll use a placeholder for migration
            default_hash = "admin_placeholder_hash"
            
            c.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@example.com', default_hash, 'System Administrator'))
            
            print("Created default admin user")
            default_user_id = c.lastrowid
        else:
            # Get the first user as the default owner for existing data
            c.execute('SELECT id FROM users LIMIT 1')
            default_user_id = c.fetchone()[0]
        
        # Check if employees table exists and if user_id column is present
        c.execute("PRAGMA table_info(employees)")
        columns = [column[1] for column in c.fetchall()]
        
        if "employees" in [table[0] for table in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            if "user_id" not in columns:
                print("Migrating employees table...")
                
                # Create a new employees table with user_id column
                c.execute('''
                    CREATE TABLE IF NOT EXISTS employees_new (
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
                
                # Copy existing data to new table and assign the default user_id
                c.execute('''
                    INSERT INTO employees_new (
                        user_id, staff_id, email, full_name, department, job_title,
                        annual_gross_pay, start_date, end_date, contract_type,
                        reimbursements, other_deductions, voluntary_pension,
                        rsa_pin, account_number, created_at
                    )
                    SELECT 
                        ?, staff_id, email, full_name, department, job_title,
                        annual_gross_pay, start_date, end_date, contract_type,
                        reimbursements, other_deductions, voluntary_pension,
                        rsa_pin, account_number, created_at
                    FROM employees
                ''', (default_user_id,))
                
                # Drop old table and rename new one
                c.execute('DROP TABLE employees')
                c.execute('ALTER TABLE employees_new RENAME TO employees')
                
                print(f"Assigned {c.rowcount} employees to user ID {default_user_id}")
        else:
            # Create employees table if it doesn't exist
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
            print("Created employees table with user_id column")
        
        # Create or update payroll_periods table
        c.execute('''
            CREATE TABLE IF NOT EXISTS payroll_periods_new (
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
        
        # Check if payroll_periods exists and migrate data
        if "payroll_periods" in [table[0] for table in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            c.execute("PRAGMA table_info(payroll_periods)")
            columns = [column[1] for column in c.fetchall()]
            
            if "user_id" not in columns:
                print("Migrating payroll_periods table...")
                
                # Get existing periods and insert one by one to handle duplicates
                c.execute('SELECT period_name, start_date, end_date, status, created_at, closed_at FROM payroll_periods')
                periods = c.fetchall()
                
                # Track processed periods to avoid duplicates
                processed_periods = set()
                period_count = 0
                
                for period in periods:
                    period_name = period[0]
                    
                    # Skip duplicates by adding a suffix if needed
                    original_name = period_name
                    counter = 1
                    while period_name in processed_periods:
                        period_name = f"{original_name} ({counter})"
                        counter += 1
                    
                    processed_periods.add(period_name)
                    
                    # Insert with potentially modified period name
                    c.execute('''
                        INSERT INTO payroll_periods_new (
                            user_id, period_name, start_date, end_date, status, created_at, closed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (default_user_id, period_name, period[1], period[2], period[3], period[4], period[5]))
                    
                    period_count += 1
                
                # Drop old table and rename new one
                c.execute('DROP TABLE payroll_periods')
                c.execute('ALTER TABLE payroll_periods_new RENAME TO payroll_periods')
                
                print(f"Migrated {period_count} payroll periods to user ID {default_user_id}")
        else:
            # Rename the new table to the original name if it didn't exist
            c.execute('ALTER TABLE payroll_periods_new RENAME TO payroll_periods')
            print("Created payroll_periods table with user_id column")
        
        # Create or update payroll_runs table
        c.execute('''
            CREATE TABLE IF NOT EXISTS payroll_runs_new (
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
        
        # Check if payroll_runs exists and migrate data
        if "payroll_runs" in [table[0] for table in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            c.execute("PRAGMA table_info(payroll_runs)")
            columns = [column[1] for column in c.fetchall()]
            
            if "user_id" not in columns:
                print("Migrating payroll_runs table...")
                
                # Copy existing data to new table
                c.execute('''
                    INSERT INTO payroll_runs_new (
                        user_id, period_id, run_date, status, approved_by, approved_at, created_at
                    )
                    SELECT 
                        ?, period_id, run_date, status, approved_by, approved_at, created_at
                    FROM payroll_runs
                ''', (default_user_id,))
                
                # Drop old table and rename new one
                c.execute('DROP TABLE payroll_runs')
                c.execute('ALTER TABLE payroll_runs_new RENAME TO payroll_runs')
                
                print(f"Assigned {c.rowcount} payroll runs to user ID {default_user_id}")
        else:
            # Rename the new table to the original name if it didn't exist
            c.execute('ALTER TABLE payroll_runs_new RENAME TO payroll_runs')
            print("Created payroll_runs table with user_id column")
        
        # Create payroll_details table if it doesn't exist (it already has foreign keys to the other tables)
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
        
        # Commit all changes
        conn.commit()
        print("Database migration completed successfully")
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error during migration: {str(e)}")
    finally:
        # Close connection
        conn.close()

if __name__ == "__main__":
    migrate_database()