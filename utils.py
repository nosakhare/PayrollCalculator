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
        'END DATE'
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
        'END DATE': [datetime.now().strftime('%Y-%m-%d')]
    }

    df = pd.DataFrame(example_data)
    return df.to_csv(index=False).encode('utf-8')