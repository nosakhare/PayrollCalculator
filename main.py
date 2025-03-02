import streamlit as st
import pandas as pd
import numpy as np
from salary_calculator import SalaryCalculator
from utils import validate_csv, validate_percentages, generate_csv_template
import io
from datetime import datetime

st.set_page_config(
    page_title="Salary Calculation System",
    page_icon="💰",
    layout="wide"
)

# Load custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("Professional Salary Calculation System")

    # Initialize session state
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'calculated_results' not in st.session_state:
        st.session_state.calculated_results = None
    if 'single_calculation_result' not in st.session_state:
        st.session_state.single_calculation_result = None

    # Sidebar for component configuration
    st.sidebar.header("Salary Component Configuration")

    components = {
        "BASIC": st.sidebar.number_input("Basic (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1),
        "TRANSPORT": st.sidebar.number_input("Transport (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1),
        "HOUSING": st.sidebar.number_input("Housing (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1),
        "UTILITY": st.sidebar.number_input("Utility (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1),
        "MEAL": st.sidebar.number_input("Meal (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1),
        "CLOTHING": st.sidebar.number_input("Clothing (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
    }

    # Validate percentages
    total_percentage = sum(components.values())
    st.sidebar.metric("Total Percentage", f"{total_percentage}%")

    if not validate_percentages(total_percentage):
        st.sidebar.error("Total percentage must equal 100%")
        return

    # Create tabs for different calculation methods
    tab1, tab2 = st.tabs(["Bulk Upload", "Single Employee"])

    with tab1:
        st.subheader("Upload Employee Data")

        # Add template download button
        template_data = generate_csv_template()
        st.download_button(
            label="📥 Download CSV Template",
            data=template_data,
            file_name="salary_template.csv",
            mime="text/csv",
            help="Download a template CSV file with the required columns"
        )

        st.markdown("---")

        uploaded_file = st.file_uploader(
            "Upload CSV file with employee data",
            type=['csv'],
            help="Required columns: Account Number, STAFF ID, Email, NAME, DEPARTMENT, JOB TITLE, ANNUAL GROSS PAY, START DATE, END DATE"
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                validation_result = validate_csv(df)

                if validation_result['valid']:
                    st.session_state.uploaded_data = df
                    st.success("File uploaded successfully!")

                    # Preview uploaded data
                    st.subheader("Data Preview")
                    st.dataframe(df.head(), use_container_width=True)

                    # Process calculations
                    if st.button("Calculate Salaries"):
                        with st.spinner("Processing salaries for all employees..."):
                            calculator = SalaryCalculator(components)
                            results = calculator.process_dataframe(df)
                            st.session_state.calculated_results = results

                            # Display results
                            st.subheader("Calculation Results")
                            st.dataframe(results.head(), use_container_width=True)

                            # Export option
                            if st.download_button(
                                label="Download Results CSV",
                                data=results.to_csv(index=False).encode('utf-8'),
                                file_name="salary_calculations.csv",
                                mime="text/csv"
                            ):
                                st.success("Download started!")
                else:
                    st.error(f"Invalid CSV structure: {validation_result['message']}")

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    with tab2:
        st.subheader("Single Employee Calculation")

        # Form for single employee data
        with st.form("single_employee_form"):
            col1, col2 = st.columns(2)

            with col1:
                job_title = st.text_input("Job Title", key="single_job")
                annual_gross = st.number_input("Annual Gross Pay", min_value=0.0, value=0.0, key="single_gross")
                contract_type = st.selectbox("Contract Type", ["Full Time", "Contract"], key="single_contract")

            with col2:
                start_date = st.date_input("Start Date", key="single_start")
                end_date = st.date_input("End Date", key="single_end")

            col3, col4 = st.columns(2)
            with col3:
                reimbursements = st.number_input("Reimbursements", min_value=0.0, value=0.0, key="single_reimburse")
                other_deductions = st.number_input("Other Deductions", min_value=0.0, value=0.0, key="single_deduct")

            with col4:
                voluntary_pension = st.number_input("Voluntary Pension", min_value=0.0, value=0.0, key="single_vol_pension")

            submitted = st.form_submit_button("Calculate Salary")

            if submitted:
                # Create a single-row DataFrame with empty values for optional fields
                single_employee_data = pd.DataFrame([{
                    'Account Number': '',
                    'STAFF ID': '',
                    'Email': '',
                    'NAME': '',
                    'DEPARTMENT': '',
                    'JOB TITLE': job_title,
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
            st.subheader("Calculation Results")
            result = st.session_state.single_calculation_result.iloc[0]

            # Create an organized display of results
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### Gross Pay")
                st.write(f"Monthly Gross: ₦{result['MONTHLY_GROSS']:,.2f}")
                st.write(f"Prorated Monthly: ₦{result['PRORATED_MONTHLY_GROSS']:,.2f}")
                st.write(f"Working Days Ratio: {result['WORKING_DAYS_RATIO']:.2%}")

            with col2:
                st.markdown("### Components")
                st.write(f"Basic: ₦{result['COMP_BASIC']:,.2f}")
                st.write(f"Transport: ₦{result['COMP_TRANSPORT']:,.2f}")
                st.write(f"Housing: ₦{result['COMP_HOUSING']:,.2f}")
                st.write(f"Utility: ₦{result['COMP_UTILITY']:,.2f}")
                st.write(f"Meal: ₦{result['COMP_MEAL']:,.2f}")
                st.write(f"Clothing: ₦{result['COMP_CLOTHING']:,.2f}")

            with col3:
                st.markdown("### Deductions & Net")
                st.write(f"PAYE Tax: ₦{result['PAYE_TAX']:,.2f}")
                st.write(f"Pension (Employee): ₦{result['MANDATORY_PENSION']:,.2f}")
                st.write(f"Pension (Employer): ₦{result['EMPLOYER_PENSION']:,.2f}")
                st.write(f"Voluntary Pension: ₦{result['VOLUNTARY_PENSION']:,.2f}")
                st.write(f"Other Deductions: ₦{result['OTHER_DEDUCTIONS']:,.2f}")
                st.markdown(f"**Net Pay: ₦{result['NET_PAY']:,.2f}**")

    # Instructions
    with st.expander("How to Use"):
        st.markdown("""
        ### Bulk Upload Method:
        1. Download the CSV template using the button above
        2. Fill in the template with your employee data
        3. Configure salary component percentages in the sidebar
        4. Upload your completed CSV file
        5. Review the data preview
        6. Click 'Calculate Salaries' to process all employees
        7. Download the results

        ### Single Employee Method:
        1. Configure salary component percentages in the sidebar
        2. Fill in the employee details in the form
        3. Click 'Calculate Salary' to see the results

        **Required Fields:**
        - Account Number
        - Staff ID
        - Email
        - Name
        - Department
        - Job Title
        - Annual Gross Pay
        - Contract Type
        - Start Date
        - End Date

        **Optional Fields:**
        - Reimbursements (additional payments/allowances)
        - Other Deductions (miscellaneous deductions)
        - Voluntary Pension (additional contribution)

        **Pension Rules:**
        - Only full-time employees are eligible for pension
        - Pension is not calculated for salaries below ₦30,000
        - Employee contribution is 8% of pensionable earnings
        - Employer contribution starts at 10% minimum
        - Voluntary pension cannot exceed 1/3 of monthly salary
        - Pensionable earnings = Basic Salary + Housing + Transport

        **Note:** Contract employees are not subject to pension deductions.
        """)

if __name__ == "__main__":
    main()