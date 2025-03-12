import streamlit as st
import pandas as pd
from datetime import datetime
from salary_calculator import SalaryCalculator
from payslip_generator import PayslipGenerator
from utils import validate_percentages, generate_csv_template
import os

def render_salary_calculator():
    st.title("Simple Salary Calculator for Nigerian Employees")

    # Initialize session state
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'calculated_results' not in st.session_state:
        st.session_state.calculated_results = None
    if 'single_calculation_result' not in st.session_state:
        st.session_state.single_calculation_result = None

    # Sidebar for component configuration
    st.sidebar.header("Customize Salary Breakdown")
    st.sidebar.write("Adjust how the salary is split between different components. These percentages affect tax and pension calculations.")

    components = {
        "BASIC": st.sidebar.number_input("Basic Salary", min_value=0.0, max_value=100.0, value=30.0, step=0.1),
        "TRANSPORT": st.sidebar.number_input("Transport", min_value=0.0, max_value=100.0, value=25.0, step=0.1),
        "HOUSING": st.sidebar.number_input("Housing", min_value=0.0, max_value=100.0, value=20.0, step=0.1),
        "UTILITY": st.sidebar.number_input("Other Benefits", min_value=0.0, max_value=100.0, value=15.0, step=0.1),
        "MEAL": st.sidebar.number_input("Meal Allowance", min_value=0.0, max_value=100.0, value=5.0, step=0.1),
        "CLOTHING": st.sidebar.number_input("Clothing Allowance", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
    }

    # Validate percentages
    total_percentage = sum(components.values())
    st.sidebar.metric("Total Percentage", f"{total_percentage}%")
    st.sidebar.write("Total must equal 100%. The breakdown affects tax calculations.")

    if not validate_percentages(total_percentage):
        st.sidebar.error("Total percentage must equal 100%")
        return

    # Create tabs for different calculation methods
    tab1, tab2 = st.tabs(["One Employee", "Multiple Employees"])

    with tab1:
        render_single_employee_calculator(components)

    with tab2:
        render_multiple_employees_calculator(components)

    # Instructions
    with st.expander("Quick Guide"):
        render_quick_guide()

def render_single_employee_calculator(components):
    st.write("Welcome! Calculate accurate salaries with proper tax and pension deductions for individual employees.")
    st.subheader("Calculate One Employee's Salary")

    # Form for single employee data
    with st.form("single_employee_form"):
        col1, col2 = st.columns(2)

        with col1:
            annual_gross = st.number_input("Yearly Salary (₦)", min_value=0.0, value=0.0, key="single_gross")
            contract_type = st.selectbox("Employment Type", ["Full Time", "Contract"], key="single_contract")

        with col2:
            start_date = st.date_input("Start Date", key="single_start")
            end_date = st.date_input("End Date", key="single_end")

        col3, col4 = st.columns(2)
        with col3:
            reimbursements = st.number_input("Extra Allowances (₦)", min_value=0.0, value=0.0, key="single_reimburse")
            other_deductions = st.number_input("Additional Deductions (₦)", min_value=0.0, value=0.0, key="single_deduct")

        with col4:
            voluntary_pension = st.number_input("Extra Pension Contribution (₦)", min_value=0.0, value=0.0, key="single_vol_pension")

        submitted = st.form_submit_button("Show Me the Results", disabled=(annual_gross <= 0))

        if submitted:
            process_single_employee_calculation(annual_gross, contract_type, start_date, end_date, 
                                             reimbursements, other_deductions, voluntary_pension, components)

    # Display calculation results and handle payslip generation
    if st.session_state.single_calculation_result is not None:
        display_single_calculation_results()
        handle_single_payslip_generation()

def render_multiple_employees_calculator(components):
    st.write("Need to process your entire team? Upload a CSV file to calculate multiple salaries at once.")
    st.subheader("Upload Your Team's Information")

    # Template download button
    csv_template = generate_csv_template()
    st.download_button(
        label="Get CSV Template",
        data=csv_template,
        file_name="employee_template.csv",
        mime="text/csv"
    )

    # File uploader and processing
    uploaded_file = st.file_uploader("Select Your File", type=["csv"])
    if uploaded_file is not None:
        process_multiple_employees_calculation(uploaded_file, components)

    # Display bulk calculation results
    if st.session_state.calculated_results is not None:
        display_bulk_calculation_results()
        handle_bulk_payslip_generation()

def render_quick_guide():
    st.markdown("""
    ### How to Calculate One Salary:
    1. Set your salary breakdown percentages in the side panel
    2. Fill in the employee information above
    3. Tap "Show Me the Results" to see the breakdown

    ### How to Calculate Multiple Salaries:
    1. Get the CSV template using the button above
    2. Add your team's information to the file
    3. Set salary breakdown percentages in the side panel
    4. Upload your completed file
    5. Check the information preview
    6. Tap "Calculate All Salaries" to process everything
    7. Download your complete results

    **Information You'll Need:**
    - Account Number (for payroll reference)
    - Staff ID (employee identifier)
    - Email (for sending pay slips)
    - Name (employee's full name)
    - Department (team or unit)
    - Yearly Salary (total annual pay)
    - Employment Type (full-time or contract)
    - Start Date (when employment began)
    - End Date (if applicable)

    **Additional Information (if applicable):**
    - Extra Allowances (transport, meals, etc.)
    - Additional Deductions (loans, advances, etc.)
    - Extra Pension Contribution (optional)

    **Important Pension Information:**
    - Only full-time employees get pension benefits
    - No pension deductions for salaries below ₦30,000
    - Employees contribute 8% of qualifying pay
    - Your company contributes at least 10% for each employee
    - Extra pension contributions can't be more than 1/3 of monthly pay
    - Qualifying pay includes: Basic Salary + Housing + Transport

    Note: Contract employees don't have pension deductions.
    """)

# Helper functions for calculations and display
def process_single_employee_calculation(annual_gross, contract_type, start_date, end_date, 
                                     reimbursements, other_deductions, voluntary_pension, components):
    single_employee_data = pd.DataFrame([{
        'Account Number': '',
        'STAFF ID': '',
        'Email': '',
        'NAME': '',
        'DEPARTMENT': '',
        'JOB TITLE': '',
        'ANNUAL GROSS PAY': annual_gross,
        'Contract Type': contract_type,
        'START DATE': start_date.strftime('%Y-%m-%d'),
        'END DATE': end_date.strftime('%Y-%m-%d'),
        'Reimbursements': reimbursements,
        'Other Deductions': other_deductions,
        'VOLUNTARY_PENSION': voluntary_pension
    }])

    calculator = SalaryCalculator(components)
    result = calculator.process_dataframe(single_employee_data)
    st.session_state.single_calculation_result = result

def display_single_calculation_results():
    result = st.session_state.single_calculation_result.iloc[0]
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Monthly Gross", f"₦{result['MONTHLY_GROSS']:,.2f}")
        st.metric("Prorated Monthly", f"₦{result['PRORATED_MONTHLY_GROSS']:,.2f}")
        st.metric("Working Days Ratio", f"{result['WORKING_DAYS_RATIO'] * 100:.1f}%")
    
    with col2:
        st.metric("PAYE Tax", f"₦{result['PAYE_TAX']:,.2f}")
        st.metric("Total Deductions", f"₦{result['TOTAL_DEDUCTIONS']:,.2f}")
        st.metric("Net Pay", f"₦{result['NET_PAY']:,.2f}")

    # Create tabs for detailed breakdown
    details_tab1, details_tab2, details_tab3 = st.tabs(["Components", "Deductions", "Tax"])
    display_detailed_breakdown(result, details_tab1, details_tab2, details_tab3)

def display_detailed_breakdown(result, components_tab, deductions_tab, tax_tab):
    with components_tab:
        st.subheader("Salary Components")
        component_data = {
            "Component": ["Basic", "Transport", "Housing", "Utility"],
            "Amount": [
                f"₦{result['COMP_BASIC']:,.2f}",
                f"₦{result['COMP_TRANSPORT']:,.2f}",
                f"₦{result['COMP_HOUSING']:,.2f}",
                f"₦{result['COMP_UTILITY']:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(component_data))

    with deductions_tab:
        st.subheader("Deductions")
        deduction_data = {
            "Deduction": ["Employee Pension", "Voluntary Pension", "PAYE Tax", "Other Deductions",
                         "Total Deductions"],
            "Amount": [
                f"₦{result['MANDATORY_PENSION']:,.2f}",
                f"₦{result['VOLUNTARY_PENSION']:,.2f}",
                f"₦{result['PAYE_TAX']:,.2f}",
                f"₦{result['OTHER_DEDUCTIONS']:,.2f}",
                f"₦{result['TOTAL_DEDUCTIONS']:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(deduction_data))

    with tax_tab:
        st.subheader("Tax Details")
        tax_data = {
            "Item": ["Consolidated Relief Allowance (CRA)", "Taxable Pay", "Tax Relief", "PAYE Tax"],
            "Amount": [
                f"₦{result['CRA']:,.2f}",
                f"₦{result['TAXABLE_PAY']:,.2f}",
                f"₦{result['TAX_RELIEF']:,.2f}",
                f"₦{result['PAYE_TAX']:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(tax_data))

def process_multiple_employees_calculation(uploaded_file, components):
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.uploaded_data = df

        # Show preview of uploaded data
        st.subheader("Data Preview")
        st.dataframe(df.head())

        # Button to process data
        if st.button("Calculate All Salaries"):
            calculator = SalaryCalculator(components)
            results = calculator.process_dataframe(df)
            st.session_state.calculated_results = results

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def handle_single_payslip_generation():
    st.subheader("Company Information for Payslip")
    company_name = st.text_input("Company Name", value="Your Company Name")
    company_address = st.text_area("Company Address", value="Company Address", height=100)
    rc_number = st.text_input("RC Number", value="RC123456")

    if st.button("Generate Payslip"):
        generate_single_payslip(company_name, company_address, rc_number)

def handle_bulk_payslip_generation():
    st.subheader("Company Information for Payslips")
    company_name = st.text_input("Company Name", value="Your Company Name", key="bulk_company_name")
    company_address = st.text_area("Company Address", value="Company Address", height=100, key="bulk_company_address")
    rc_number = st.text_input("RC Number", value="RC123456", key="bulk_rc_number")

    if st.button("Generate All Payslips"):
        generate_bulk_payslips(company_name, company_address, rc_number)

def generate_single_payslip(company_name, company_address, rc_number):
    try:
        result = st.session_state.single_calculation_result.iloc[0]
        employee_data = create_employee_data_for_payslip(result, company_name, company_address, rc_number)
        
        generator = PayslipGenerator()
        payslip_path = generator.generate_payslip(employee_data)

        with open(payslip_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        st.download_button(
            label="Download Payslip",
            data=pdf_bytes,
            file_name=f"payslip_{datetime.now().strftime('%Y%m')}.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error generating payslip: {str(e)}")

def generate_bulk_payslips(company_name, company_address, rc_number):
    try:
        generator = PayslipGenerator()
        payslip_dir = "payslips"
        os.makedirs(payslip_dir, exist_ok=True)

        for index, row in st.session_state.calculated_results.iterrows():
            employee_data = create_employee_data_for_payslip(row, company_name, company_address, rc_number, index)
            generator.generate_payslip(employee_data, payslip_dir)

        create_and_offer_zip_download()

    except Exception as e:
        st.error(f"Error generating payslips: {str(e)}")

def create_employee_data_for_payslip(row, company_name, company_address, rc_number, index=None):
    return {
        'id': row.get('STAFF ID', f'TEMP{index + 1 if index is not None else 1}'),
        'company_info': {
            'name': company_name,
            'address': company_address,
            'rc_number': rc_number
        },
        'name': row.get('NAME', 'Employee'),
        'department': row.get('DEPARTMENT', 'Department'),
        'pay_period': datetime.now().strftime('%B %Y'),
        'salary_data': {
            'earnings': {
                'Basic Salary': row['COMP_BASIC'],
                'Transport': row['COMP_TRANSPORT'],
                'Housing': row['COMP_HOUSING'],
                'Utility': row['COMP_UTILITY'],
                'Meal Allowance': row['COMP_MEAL'],
                'Clothing Allowance': row['COMP_CLOTHING']
            },
            'deductions': {
                'PAYE Tax': row['PAYE_TAX'],
                'Pension': row['MANDATORY_PENSION'],
                'Other Deductions': row['OTHER_DEDUCTIONS']
            },
            'employer_pension': row['EMPLOYER_PENSION'],
            'net_pay': row['NET_PAY']
        }
    }

def create_and_offer_zip_download():
    import shutil
    zip_path = "payslips.zip"
    shutil.make_archive("payslips", 'zip', "payslips")

    with open(zip_path, "rb") as zip_file:
        st.download_button(
            label="Download All Payslips",
            data=zip_file.read(),
            file_name="payslips.zip",
            mime="application/zip"
        )
