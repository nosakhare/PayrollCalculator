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
        'Contract Type',
        'Reimbursements',
        'Other Deductions',
        'RSA_PIN',
        'VOLUNTARY_PENSION',
        'EMPLOYER_PENSION_RATE'
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
        df['VOLUNTARY_PENSION'] = pd.to_numeric(df['VOLUNTARY_PENSION']).fillna(0)
        df['EMPLOYER_PENSION_RATE'] = pd.to_numeric(df['EMPLOYER_PENSION_RATE']).fillna(10)

        # Validate pension rates and amounts
        if (df['EMPLOYER_PENSION_RATE'] < 10).any():
            return {
                'valid': False,
                'message': "Employer pension rate must be at least 10%"
            }

        # Validate voluntary pension (not exceeding 1/3 of monthly salary)
        monthly_salary = df['ANNUAL GROSS PAY'] / 12
        if (df['VOLUNTARY_PENSION'] > monthly_salary / 3).any():
            return {
                'valid': False,
                'message': "Voluntary pension cannot exceed 1/3 of monthly salary"
            }

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
    """Generate a template CSV file with example data.
    Contract Type: Must be either 'Full Time' or 'Contract'
    Reimbursements: Additional payments like allowances or reimbursements
    Other Deductions: Miscellaneous deductions from gross pay
    """
    example_data = {
        'Account Number': ['1234567890', '0987654321'],
        'STAFF ID': ['EMP001', 'CON001'],
        'Email': ['john.doe@company.com', 'jane.smith@company.com'],
        'NAME': ['John Doe', 'Jane Smith'],
        'DEPARTMENT': ['Engineering', 'Design'],
        'JOB TITLE': ['Software Engineer', 'UI Designer'],
        'ANNUAL GROSS PAY': [5000000, 4000000],
        'START DATE': [(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')],
        'END DATE': [datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')],
        'Contract Type': ['Full Time', 'Contract'],
        'Reimbursements': [50000, 25000],
        'Other Deductions': [10000, 5000],
        'RSA_PIN': ['PEN123456789', 'PEN987654321'],
        'VOLUNTARY_PENSION': [0, 0],
        'EMPLOYER_PENSION_RATE': [10, 10]
    }

    df = pd.DataFrame(example_data)
    return df.to_csv(index=False).encode('utf-8')