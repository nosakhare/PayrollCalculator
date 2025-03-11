import streamlit as st
import pandas as pd
from datetime import datetime, date
from calendar import monthrange
from database import init_db, add_employee, get_all_employees, generate_staff_id, create_payroll_period, get_active_payroll_period, create_payroll_run, save_payroll_details, update_payroll_run_status
from salary_calculator import SalaryCalculator
from utils import validate_percentages, generate_csv_template, validate_csv, process_bulk_upload
from payslip_generator import PayslipGenerator
import os

# Must be the first Streamlit command
st.set_page_config(page_title="Nigerian Salary Calculator", page_icon="💰", layout="wide")

# Initialize database
init_db()

def employee_management_page():
    st.title("Employee Management")

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Employee", "View Employees", "Bulk Upload"])

    with tab1:
        st.subheader("Add New Employee")
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)

            with col1:
                staff_id = st.text_input("Staff ID", value=generate_staff_id(), disabled=True)
                email = st.text_input("Email", key="email")
                full_name = st.text_input("Full Name", key="full_name")
                department = st.text_input("Department", key="department")

            with col2:
                job_title = st.text_input("Job Title", key="job_title")
                annual_gross = st.number_input("Annual Gross Pay (₦)", min_value=0.0, key="annual_gross")
                account_number = st.text_input("Account Number", key="account_number")
                rsa_pin = st.text_input("RSA PIN (Optional)", key="rsa_pin")

            col3, col4 = st.columns(2)
            with col3:
                contract_type = st.selectbox("Contract Type", ["Full Time", "Contract"], key="contract_type")
                start_date = st.date_input("Start Date", key="start_date")

            with col4:
                end_date = st.date_input("End Date (Optional)", key="end_date")
                reimbursements = st.number_input("Reimbursements (₦)", min_value=0.0, key="reimbursements")

            col5, col6 = st.columns(2)
            with col5:
                other_deductions = st.number_input("Other Deductions (₦)", min_value=0.0, key="other_deductions")

            with col6:
                voluntary_pension = st.number_input("Voluntary Pension (₦)", min_value=0.0, key="voluntary_pension")

            submitted = st.form_submit_button("Add Employee")

            if submitted:
                employee_data = {
                    'staff_id': staff_id,
                    'email': email,
                    'full_name': full_name,
                    'department': department,
                    'job_title': job_title,
                    'annual_gross_pay': annual_gross,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                    'contract_type': contract_type,
                    'reimbursements': reimbursements,
                    'other_deductions': other_deductions,
                    'voluntary_pension': voluntary_pension,
                    'rsa_pin': rsa_pin,
                    'account_number': account_number
                }

                success, message = add_employee(employee_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with tab2:
        st.subheader("Employee List")
        employees = get_all_employees()
        if employees:
            df = pd.DataFrame(employees)
            st.dataframe(df)
        else:
            st.info("No employees found in the system.")

    with tab3:
        st.subheader("Bulk Upload")

        # Instructions
        st.markdown("""
        ### Bulk Employee Upload Instructions
        1. Download the template and fill in your employee data
        2. Ensure all required fields are completed
        3. Upload your file for processing
        4. Review any validation errors before confirming the upload
        """)

        # Template download button
        csv_template = generate_csv_template()
        st.download_button(
            label="📥 Download CSV Template",
            data=csv_template,
            file_name="employee_template.csv",
            mime="text/csv",
            help="Download a template CSV file with example data"
        )

        # File upload
        uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)

                # Show preview of the data
                st.subheader("Data Preview")
                st.dataframe(df.head())

                # Validate the CSV data
                validation_result = validate_csv(df)

                if not validation_result['valid']:
                    st.error("Validation Errors")
                    for error in validation_result['errors']:
                        st.warning(error)
                else:
                    # Show confirmation button only if validation passes
                    if st.button("Confirm Upload"):
                        with st.spinner("Processing employee data..."):
                            results = process_bulk_upload(df)

                            if results['success']:
                                st.success(results['message'])
                            else:
                                st.error(results['message'])
                                if results['errors']:
                                    st.subheader("Error Details")
                                    for error in results['errors']:
                                        st.warning(error)

                            # Provide option to start over
                            if st.button("Upload Another File"):
                                st.experimental_rerun()

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

def salary_calculator_page():
    # Check if the request is for ads.txt
    path = st.query_params.get("path", [""])[0]
    if path == "ads.txt":
        st.write("google.com, pub-4067343505079138, DIRECT, f08c47fec0942fa0")
        st.stop()

    st.sidebar.image("generated-icon.png", width=100)
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

    # Add new description
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
        # Add welcome message
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

            # Only enable the button if annual_gross is greater than zero
            submitted = st.form_submit_button("Show Me the Results", disabled=(annual_gross <= 0))

            if submitted:
                # Create a single-row DataFrame with empty values for optional fields
                single_employee_data = pd.DataFrame([{
                    'Account Number': '',
                    'STAFF ID': '',
                    'Email': '',
                    'NAME': '',
                    'DEPARTMENT': '',
                    'JOB TITLE': '',  # Now also empty as it's optional
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

        # Display single calculation results
        if st.session_state.single_calculation_result is not None:
            st.subheader("Your Salary Breakdown")
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

            with details_tab1:
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

            with details_tab2:
                st.subheader("Deductions")
                deduction_data = {
                    "Deduction": ["Employee Pension", "Voluntary Pension", "PAYE Tax", "Other Deductions", "Total Deductions"],
                    "Amount": [
                        f"₦{result['MANDATORY_PENSION']:,.2f}",
                        f"₦{result['VOLUNTARY_PENSION']:,.2f}",
                        f"₦{result['PAYE_TAX']:,.2f}",
                        f"₦{result['OTHER_DEDUCTIONS']:,.2f}",
                        f"₦{result['TOTAL_DEDUCTIONS']:,.2f}"
                    ]
                }
                st.dataframe(pd.DataFrame(deduction_data))

            with details_tab3:
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

            # Additional info
            st.write("Note: Employer contribution to pension: ", f"₦{result['EMPLOYER_PENSION']:,.2f}")

            # Company Information Form moved here
            st.subheader("Company Information for Payslip")
            company_name = st.text_input("Company Name", value="Your Company Name")
            company_address = st.text_area("Company Address", value="Company Address", height=100)
            rc_number = st.text_input("RC Number", value="RC123456")

            # Button to generate payslip
            if st.button("Generate Payslip"):
                try:
                    # Create employee data dictionary for payslip
                    employee_data = {
                        'id': 'TEMP001',  # Temporary ID for single calculation
                        'company_info': {
                            'name': company_name,
                            'address': company_address,
                            'rc_number': rc_number
                        },
                        'name': 'Employee',
                        'department': 'Department',
                        'pay_period': datetime.now().strftime('%B %Y'),
                        'salary_data': {
                            'earnings': {
                                'Basic Salary': result['COMP_BASIC'],
                                'Transport': result['COMP_TRANSPORT'],
                                'Housing': result['COMP_HOUSING'],
                                'Utility': result['COMP_UTILITY'],
                                'Meal Allowance': result['COMP_MEAL'],
                                'Clothing Allowance': result['COMP_CLOTHING']
                            },
                            'deductions': {
                                'PAYE Tax': result['PAYE_TAX'],
                                'Pension': result['MANDATORY_PENSION'],
                                'Other Deductions': result['OTHER_DEDUCTIONS']
                            },
                            'employer_pension': result['EMPLOYER_PENSION'],
                            'net_pay': result['NET_PAY']
                        }
                    }

                    # Generate payslip
                    generator = PayslipGenerator()
                    payslip_path = generator.generate_payslip(employee_data)

                    # Read the generated PDF for download
                    with open(payslip_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()

                    # Add download button
                    st.download_button(
                        label="Download Payslip",
                        data=pdf_bytes,
                        file_name=f"payslip_{datetime.now().strftime('%Y%m')}.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"Error generating payslip: {str(e)}")

            # Button to calculate another salary
            if st.button("Start a New Calculation"):
                st.session_state.single_calculation_result = None
                st.experimental_rerun()

    with tab2:
        # Add welcome message
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

        # File uploader
        uploaded_file = st.file_uploader("Select Your File", type=["csv"])

        if uploaded_file is not None:
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

        # Display bulk calculation results
        if st.session_state.calculated_results is not None:
            st.subheader("Your Salary Breakdown")
            st.dataframe(st.session_state.calculated_results)

            # Company Information Form moved here for bulk generation
            st.subheader("Company Information for Payslips")
            bulk_company_name = st.text_input("Company Name", value="Your Company Name", key="bulk_company_name")
            bulk_company_address = st.text_area("Company Address", value="Company Address", height=100, key="bulk_company_address")
            bulk_rc_number = st.text_input("RC Number", value="RC123456", key="bulk_rc_number")

            # Add bulk payslip generation button
            if st.button("Generate All Payslips"):
                try:
                    generator = PayslipGenerator()
                    payslip_dir = "payslips"
                    os.makedirs(payslip_dir, exist_ok=True)

                    # Generate payslips for all employees
                    for index, row in st.session_state.calculated_results.iterrows():
                        employee_data = {
                            'id': row.get('STAFF ID', f'TEMP{index+1}'),
                            'company_info': {
                                'name': bulk_company_name,
                                'address': bulk_company_address,
                                'rc_number': bulk_rc_number
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
                        generator.generate_payslip(employee_data, payslip_dir)

                    # Create ZIP file of all payslips
                    import shutil
                    zip_path = "payslips.zip"
                    shutil.make_archive("payslips", 'zip', payslip_dir)

                    # Offer ZIP download
                    with open(zip_path, "rb") as zip_file:
                        st.download_button(
                            label="Download All Payslips",
                            data=zip_file.read(),
                            file_name="payslips.zip",
                            mime="application/zip"
                        )

                except Exception as e:
                    st.error(f"Error generating payslips: {str(e)}")

            # Download button for results
            csv_results = st.session_state.calculated_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Save Results",
                data=csv_results,
                file_name="salary_results.csv",
                mime="text/csv"
            )

            # Button to calculate again
            if st.button("Start a New Calculation"):
                st.session_state.uploaded_data = None
                st.session_state.calculated_results = None
                st.experimental_rerun()

    # Instructions
    with st.expander("Quick Guide"):
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


def payroll_processing_page():
    st.title("Payroll Processing")

    # Create tabs for different payroll operations
    tab1, tab2, tab3 = st.tabs(["Create Payroll Period", "Process Payroll", "Approval & History"])

    with tab1:
        st.subheader("Create New Payroll Period")

        # Form for creating new payroll period
        with st.form("create_period_form"):
            # Get current month and year
            today = date.today()
            current_month = today.strftime('%B %Y')

            period_name = st.text_input("Period Name", value=current_month)
            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input("Start Date", 
                    value=date(today.year, today.month, 1))

            with col2:
                # Get last day of current month
                _, last_day = monthrange(today.year, today.month)
                end_date = st.date_input("End Date", 
                    value=date(today.year, today.month, last_day))

            submitted = st.form_submit_button("Create Payroll Period")

            if submitted:
                success, message = create_payroll_period(
                    period_name,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with tab2:
        st.subheader("Process Payroll")

        # Get active payroll period
        active_period = get_active_payroll_period()

        if active_period:
            st.info(f"Active Period: {active_period['period_name']}")

            # Get all employees
            employees = get_all_employees()

            if employees:
                # Multi-select for employees
                selected_employees = st.multiselect(
                    "Select Employees for Payroll Processing",
                    options=[emp['staff_id'] for emp in employees],
                    format_func=lambda x: next(emp['full_name'] for emp in employees if emp['staff_id'] == x)
                )

                if selected_employees:
                    if st.button("Process Selected Employees"):
                        success, run_id = create_payroll_run(active_period['id'])

                        if success:
                            calculator = SalaryCalculator({
                                "BASIC": 30.0,
                                "TRANSPORT": 25.0,
                                "HOUSING": 20.0,
                                "UTILITY": 15.0,
                                "MEAL": 5.0,
                                "CLOTHING": 5.0
                            })

                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            for i, staff_id in enumerate(selected_employees):
                                employee = next(emp for emp in employees if emp['staff_id'] == staff_id)

                                # Create DataFrame for single employee
                                emp_df = pd.DataFrame([{
                                    'Account Number': employee['account_number'],
                                    'STAFF ID': employee['staff_id'],
                                    'Email': employee['email'],
                                    'NAME': employee['full_name'],
                                    'DEPARTMENT': employee['department'],
                                    'JOB TITLE': employee['job_title'],
                                    'ANNUAL GROSS PAY': employee['annual_gross_pay'],
                                    'Contract Type': employee['contract_type'],
                                    'START DATE': employee['start_date'],
                                    'END DATE': employee['end_date'] or datetime.now().strftime('%Y-%m-%d'),
                                    'Reimbursements': employee['reimbursements'],
                                    'Other Deductions': employee['other_deductions'],
                                    'VOLUNTARY_PENSION': employee['voluntary_pension']
                                }])

                                # Calculate salary
                                result = calculator.process_dataframe(emp_df).iloc[0]

                                # Save payroll details
                                payroll_details = {
                                    'employee_id': employee['id'],
                                    'gross_pay': result['MONTHLY_GROSS'],
                                    'net_pay': result['NET_PAY'],
                                    'basic_salary': result['COMP_BASIC'],
                                    'housing': result['COMP_HOUSING'],
                                    'transport': result['COMP_TRANSPORT'],
                                    'utility': result['COMP_UTILITY'],
                                    'meal': result['COMP_MEAL'],
                                    'clothing': result['COMP_CLOTHING'],
                                    'pension_employee': result['MANDATORY_PENSION'],
                                    'pension_employer': result['EMPLOYER_PENSION'],
                                    'pension_voluntary': result['VOLUNTARY_PENSION'],
                                    'paye_tax': result['PAYE_TAX'],
                                    'other_deductions': result['OTHER_DEDUCTIONS'],
                                    'reimbursements': result['REIMBURSEMENTS']
                                }

                                save_success, save_message = save_payroll_details(run_id, payroll_details)

                                # Update progress
                                progress = (i + 1) / len(selected_employees)
                                progress_bar.progress(progress)
                                status_text.text(f"Processing {i+1}/{len(selected_employees)}: {employee['full_name']}")

                            # Update run status to pending approval
                            update_payroll_run_status(run_id, 'pending_approval')

                            st.success("Payroll processing completed and sent for approval!")
                        else:
                            st.error(f"Failed to create payroll run: {run_id}")
                else:
                    st.warning("Please select at least one employee to process payroll.")
            else:
                st.warning("No employees found in the system.")
        else:
            st.error("No active payroll period found. Please create a new period first.")

    with tab3:
        st.subheader("Payroll Approval & History")
        # TODO: Add approval workflow and history view

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", [
        "Salary Calculator",
        "Employee Management",
        "Payroll Processing"  # Add new page option
    ])

    if page == "Salary Calculator":
        salary_calculator_page()
    elif page == "Employee Management":
        employee_management_page()
    else:
        payroll_processing_page()

if __name__ == "__main__":
    st.markdown("""
    <style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    try:
        with open("styles.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    main()