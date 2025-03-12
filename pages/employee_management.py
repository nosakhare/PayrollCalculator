import streamlit as st
import pandas as pd
from database import add_employee, get_all_employees, generate_staff_id
from utils import validate_csv, process_bulk_upload, generate_csv_template

def render_employee_management():
    st.title("Employee Management")

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Employee", "View Employees", "Bulk Upload"])

    with tab1:
        render_add_employee()

    with tab2:
        render_view_employees()

    with tab3:
        render_bulk_upload()

def render_add_employee():
    st.subheader("Add New Employee")
    with st.form("add_employee_form"):
        # Required Fields Section
        st.subheader("Required Information")
        col1, col2 = st.columns(2)

        with col1:
            staff_id = st.text_input("Staff ID", value=generate_staff_id(), disabled=True)
            email = st.text_input("Email *", key="email")
            full_name = st.text_input("Full Name *", key="full_name")
            department = st.text_input("Department *", key="department")

        with col2:
            job_title = st.text_input("Job Title *", key="job_title")
            annual_gross = st.number_input("Annual Gross Pay (₦) *", min_value=0.0, key="annual_gross")
            account_number = st.text_input("Account Number *", key="account_number")

        col3, col4 = st.columns(2)
        with col3:
            contract_type = st.selectbox("Contract Type *", ["Full Time", "Contract"], key="contract_type")
            start_date = st.date_input("Start Date *", key="start_date")

        with col4:
            end_date = st.date_input("End Date (Optional)", key="end_date")
            rsa_pin = st.text_input("RSA PIN (Optional)", key="rsa_pin")

        # Optional Fields Section
        st.markdown("---")
        st.subheader("Optional Details")
        st.info("These fields can be updated later during payroll review.")

        col5, col6 = st.columns(2)
        with col5:
            reimbursements = st.number_input("Reimbursements (₦)",
                                          min_value=0.0,
                                          value=0.0,
                                          help="Additional allowances like transport or meal allowances",
                                          key="reimbursements"
                                          )

        with col6:
            other_deductions = st.number_input("Other Deductions (₦)",
                                            min_value=0.0,
                                            value=0.0,
                                            help="Additional deductions like loans or advances",
                                            key="other_deductions"
                                            )

        voluntary_pension = st.number_input("Voluntary Pension (₦)",
                                         min_value=0.0,
                                         value=0.0,
                                         help="Additional voluntary pension contributions",
                                         key="voluntary_pension"
                                         )

        submitted = st.form_submit_button("Add Employee")

        if submitted:
            if not email or not full_name or not department or not job_title or not annual_gross or not account_number:
                st.error("Please fill in all required fields marked with *")
                return

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

def render_view_employees():
    st.subheader("Employee List")
    employees = get_all_employees()
    if employees:
        df = pd.DataFrame(employees)
        st.dataframe(df)
    else:
        st.info("No employees found in the system.")

def render_bulk_upload():
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
                            st.rerun()

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
