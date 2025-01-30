import pandas as pd
import io
from datetime import datetime, timedelta

def validate_csv(df):
    """Validate uploaded CSV structure and data types."""
    required_columns = [
        'Account Number',
        'STAFF ID',
        'Email',
        'NAME',
        'DEPARTMENT',
        'JOB TITLE',
        'ANNUAL GROSS PAY',
        'START DATE',
        'END DATE',
        'Contract Type',  # New column
        'Reimbursements',  # New column
        'Other Deductions'  # New column
    ]

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return {
            'valid': False,
            'message': f"Missing required columns: {', '.join(missing_columns)}"
        }

    # Validate data types
    try:
        df['ANNUAL GROSS PAY'] = pd.to_numeric(df['ANNUAL GROSS PAY'])
        df['START DATE'] = pd.to_datetime(df['START DATE'])
        df['END DATE'] = pd.to_datetime(df['END DATE'])
        df['Reimbursements'] = pd.to_numeric(df['Reimbursements']).fillna(0)
        df['Other Deductions'] = pd.to_numeric(df['Other Deductions']).fillna(0)

        # Validate Contract Type
        valid_contract_types = ['Full Time', 'Contract']
        invalid_types = df[~df['Contract Type'].isin(valid_contract_types)]['Contract Type'].unique()
        if len(invalid_types) > 0:
            return {
                'valid': False,
                'message': f"Invalid contract types found: {', '.join(invalid_types)}. Must be either 'Full Time' or 'Contract'"
            }
    except Exception as e:
        return {
            'valid': False,
            'message': f"Data type validation failed: {str(e)}"
        }

    return {'valid': True, 'message': "Validation successful"}

def validate_percentages(total):
    """Validate that component percentages sum to 100%."""
    return abs(total - 100.0) < 0.01

def generate_csv_template():
    """Generate a template CSV file with example data."""
    example_data = {
        'Account Number': ['1234567890'],
        'STAFF ID': ['EMP001'],
        'Email': ['john.doe@company.com'],
        'NAME': ['John Doe'],
        'DEPARTMENT': ['Engineering'],
        'JOB TITLE': ['Software Engineer'],
        'ANNUAL GROSS PAY': [5000000],
        'START DATE': [(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')],
        'END DATE': [datetime.now().strftime('%Y-%m-%d')],
        'Contract Type': ['Full Time'],
        'Reimbursements': [0],
        'Other Deductions': [0]
    }

    df = pd.DataFrame(example_data)
    return df.to_csv(index=False).encode('utf-8')