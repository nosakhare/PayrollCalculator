    from typing import Dict, List, TypedDict, Optional
    import pandas as pd
    import io
    from datetime import datetime, timedelta
    from decimal import Decimal
    import logging

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    class ValidationResult(TypedDict):
        valid: bool
        message: str

    class CSVValidator:
        """Handles CSV validation and template generation for payroll data."""

        REQUIRED_COLUMNS: List[str] = [
            'Account Number', 'STAFF ID', 'Email', 'NAME', 'DEPARTMENT',
            'JOB TITLE', 'ANNUAL GROSS PAY', 'START DATE', 'END DATE',
            'Contract Type', 'Reimbursements', 'Other Deductions', 'VOLUNTARY_PENSION'
        ]

        VALID_CONTRACT_TYPES: List[str] = ['Full Time', 'Contract']
        MAX_PENSION_RATIO: float = 1/3

        @classmethod
        def validate_csv(cls, df: pd.DataFrame) -> ValidationResult:
            """
            Validate uploaded CSV structure and data types.

            Args:
                df: pandas DataFrame containing the CSV data

            Returns:
                ValidationResult indicating success/failure with message
            """
            try:
                logger.info("Starting CSV validation")

                # Check for required columns
                missing_columns = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
                if missing_columns:
                    return {
                        'valid': False,
                        'message': f"Missing required columns: {', '.join(missing_columns)}"
                    }

                # Convert and validate numeric columns
                numeric_columns = {
                    'ANNUAL GROSS PAY': True,  # True means required
                    'Reimbursements': False,   # False means optional (can be NaN)
                    'Other Deductions': False,
                    'VOLUNTARY_PENSION': False
                }

                for col, required in numeric_columns.items():
                    try:
                        df[col] = pd.to_numeric(df[col])
                        if not required:
                            df[col] = df[col].fillna(0)
                    except Exception as e:
                        return {
                            'valid': False,
                            'message': f"Invalid numeric value in column {col}: {str(e)}"
                        }

                # Validate dates
                date_columns = ['START DATE', 'END DATE']
                for col in date_columns:
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception as e:
                        return {
                            'valid': False,
                            'message': f"Invalid date format in column {col}: {str(e)}"
                        }

                # Validate date order
                if (df['START DATE'] > df['END DATE']).any():
                    return {
                        'valid': False,
                        'message': "START DATE must be before END DATE"
                    }

                # Validate voluntary pension
                monthly_salary = df['ANNUAL GROSS PAY'] / Decimal('12')
                if (df['VOLUNTARY_PENSION'] > monthly_salary * cls.MAX_PENSION_RATIO).any():
                    return {
                        'valid': False,
                        'message': "Voluntary pension cannot exceed 1/3 of monthly salary"
                    }

                # Validate Contract Type
                invalid_types = df[~df['Contract Type'].isin(cls.VALID_CONTRACT_TYPES)]['Contract Type'].unique()
                if len(invalid_types) > 0:
                    return {
                        'valid': False,
                        'message': (f"Invalid contract types found: {', '.join(invalid_types)}. "
                                  f"Must be either {' or '.join(cls.VALID_CONTRACT_TYPES)}")
                    }

                logger.info("CSV validation successful")
                return {'valid': True, 'message': "Validation successful"}

            except Exception as e:
                logger.error(f"Validation failed: {str(e)}")
                return {
                    'valid': False,
                    'message': f"Validation failed: {str(e)}"
                }

        @staticmethod
        def generate_csv_template() -> bytes:
            """
            Generate a template CSV file with example data.

            Returns:
                UTF-8 encoded CSV data as bytes
            """
            logger.info("Generating CSV template")

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
                'END DATE': [datetime.now().strftime('%Y-%m-%d')] * 2,
                'Contract Type': ['Full Time', 'Contract'],
                'Reimbursements': [50000, 25000],
                'Other Deductions': [10000, 5000],
                'VOLUNTARY_PENSION': [0, 0]
            }

            df = pd.DataFrame(example_data)
            return df.to_csv(index=False).encode('utf-8')