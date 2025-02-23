
# Salary Calculator System

A professional payroll calculation system built with Streamlit that handles salary components, pension calculations, and tax deductions for Nigerian companies.

## Features

- Salary component breakdown (Basic, Transport, Housing, etc.)
- Pension calculations for full-time employees
- PAYE tax calculations with proper CRA
- Support for both full-time and contract employees
- Prorated salary calculations
- Bulk processing via CSV upload
- Downloadable results

## Usage

1. Configure salary components in the sidebar
2. Download the CSV template
3. Fill in employee data
4. Upload the completed CSV
5. Review data preview
6. Calculate salaries
7. Download results

## Required CSV Fields

- Account Number
- STAFF ID
- Email
- NAME
- DEPARTMENT
- JOB TITLE
- ANNUAL GROSS PAY
- START DATE (YYYY-MM-DD)
- END DATE (YYYY-MM-DD)
- Contract Type (Full Time/Contract)
- Reimbursements
- Other Deductions
- VOLUNTARY_PENSION

## Pension Rules

- Applies only to full-time employees
- Minimum salary threshold: ₦30,000
- Employee contribution: 8%
- Employer contribution: 10%
- Voluntary pension cap: 1/3 of monthly salary
- Pensionable earnings = Basic + Housing + Transport

## Running the Application

```bash
streamlit run main.py
```

The application will be available at port 5000.

## API Support

The system includes a REST API for integration. See `api_spec.md` for detailed documentation.

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy

## License

This project is proprietary and confidential.
