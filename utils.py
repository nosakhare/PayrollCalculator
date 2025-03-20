import pandas as pd
import io
from datetime import datetime, timedelta
from database import add_employee

def validate_csv(df):
    """Validate uploaded CSV structure and data types with enhanced error reporting."""
    required_columns = [
        'Account Number', 'STAFF ID', 'Email', 'NAME', 'DEPARTMENT',
        'JOB TITLE', 'ANNUAL GROSS PAY', 'START DATE', 'END DATE',
        'Contract Type', 'Reimbursements', 'Other Deductions', 'VOLUNTARY_PENSION'
    ]

    validation_errors = []

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        validation_errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return {'valid': False, 'errors': validation_errors}

    # Validate data types and content
    try:
        # Store rows with errors for reporting
        error_rows = []

        # Validate numeric fields
        numeric_fields = {
            'ANNUAL GROSS PAY': 'Annual Gross Pay must be a positive number',
            'Reimbursements': 'Reimbursements must be a number',
            'Other Deductions': 'Other Deductions must be a number',
            'VOLUNTARY_PENSION': 'Voluntary Pension must be a number'
        }

        for field, error_msg in numeric_fields.items():
            non_numeric_rows = df[pd.to_numeric(df[field], errors='coerce').isna()].index.tolist()
            if non_numeric_rows:
                error_rows.extend([f"Row {i+2}: {error_msg}" for i in non_numeric_rows])

        # Validate dates
        date_fields = {
            'START DATE': 'Start Date must be a valid date (YYYY-MM-DD)',
            'END DATE': 'End Date must be a valid date (YYYY-MM-DD) if provided'
        }

        for field, error_msg in date_fields.items():
            df[field] = pd.to_datetime(df[field], errors='coerce')
            invalid_dates = df[df[field].isna()].index.tolist()
            if invalid_dates and (field == 'START DATE' or (field == 'END DATE' and df.loc[invalid_dates, field].notna().any())):
                error_rows.extend([f"Row {i+2}: {error_msg}" for i in invalid_dates])

        # Validate contract type
        valid_contract_types = ['Full Time', 'Contract']
        invalid_types = df[~df['Contract Type'].isin(valid_contract_types)]
        if not invalid_types.empty:
            error_rows.extend([f"Row {i+2}: Invalid contract type. Must be 'Full Time' or 'Contract'" 
                             for i in invalid_types.index])

        # Validate email format
        invalid_emails = df[~df['Email'].str.contains('@', na=False)]
        if not invalid_emails.empty:
            error_rows.extend([f"Row {i+2}: Invalid email format" 
                             for i in invalid_emails.index])

        # Validate voluntary pension (not exceeding 1/3 of monthly salary)
        monthly_salary = df['ANNUAL GROSS PAY'] / 12
        invalid_pension = df[df['VOLUNTARY_PENSION'] > monthly_salary / 3]
        if not invalid_pension.empty:
            error_rows.extend([f"Row {i+2}: Voluntary pension cannot exceed 1/3 of monthly salary" 
                             for i in invalid_pension.index])

        if error_rows:
            validation_errors.extend(error_rows)
            return {'valid': False, 'errors': validation_errors}

    except Exception as e:
        validation_errors.append(f"Data validation failed: {str(e)}")
        return {'valid': False, 'errors': validation_errors}

    return {'valid': True, 'errors': []}

def process_bulk_upload(df, user_id):
    """Process bulk employee upload with duplicate handling."""
    validation_result = validate_csv(df)
    if not validation_result['valid']:
        return {
            'success': False,
            'message': "Validation failed",
            'errors': validation_result['errors']
        }

    results = {
        'success': True,
        'processed': 0,
        'errors': [],
        'updated': 0,
        'added': 0
    }

    for index, row in df.iterrows():
        try:
            employee_data = {
                'staff_id': row['STAFF ID'],
                'email': row['Email'],
                'full_name': row['NAME'],
                'department': row['DEPARTMENT'],
                'job_title': row['JOB TITLE'],
                'annual_gross_pay': float(row['ANNUAL GROSS PAY']),
                'start_date': row['START DATE'].strftime('%Y-%m-%d'),
                'end_date': row['END DATE'].strftime('%Y-%m-%d') if pd.notna(row['END DATE']) else None,
                'contract_type': row['Contract Type'],
                'reimbursements': float(row.get('Reimbursements', 0)),
                'other_deductions': float(row.get('Other Deductions', 0)),
                'voluntary_pension': float(row.get('VOLUNTARY_PENSION', 0)),
                'account_number': str(row['Account Number'])
            }

            success, message = add_employee(employee_data, user_id)
            if success:
                results['processed'] += 1
                if "updated" in message.lower():
                    results['updated'] += 1
                else:
                    results['added'] += 1
            else:
                results['errors'].append(f"Row {index + 2}: {message}")

        except Exception as e:
            results['errors'].append(f"Row {index + 2}: Unexpected error - {str(e)}")

    if results['errors']:
        results['success'] = False

    results['message'] = (
        f"Processed {results['processed']} employees "
        f"({results['added']} added, {results['updated']} updated). "
        f"{len(results['errors'])} errors occurred."
    )

    return results

def validate_percentages(total):
    """Validate that component percentages sum to 100%."""
    return abs(total - 100.0) < 0.01

def generate_csv_template():
    """Generate a template CSV file with example data."""
    example_data = {
        'Account Number': ['1234567890', '0987654321'],
        'STAFF ID': ['EMP001', 'CON001'],
        'Email': ['john.doe@company.com', 'jane.smith@company.com'],
        'NAME': ['John Doe', 'Jane Smith'],
        'DEPARTMENT': ['Engineering', 'Design'],
        'JOB TITLE': ['Software Engineer', 'UI Designer'],
        'ANNUAL GROSS PAY': [5000000, 4000000],
        'START DATE': [(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                      (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')],
        'END DATE': [datetime.now().strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d')],
        'Contract Type': ['Full Time', 'Contract'],
        'Reimbursements': [50000, 25000],
        'Other Deductions': [10000, 5000],
        'VOLUNTARY_PENSION': [0, 0]
    }

    df = pd.DataFrame(example_data)
    return df.to_csv(index=False).encode('utf-8')