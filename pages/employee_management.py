import streamlit as st
import pandas as pd
from datetime import datetime
from database import add_employee, get_all_employees, generate_staff_id, delete_employee
from utils import validate_csv, process_bulk_upload, generate_csv_template

def render_page():
    st.title("Employee Management")

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Employee", "View Employees", "Bulk Upload"])

    with tab1:
        st.subheader("Add New Employee")
        # Changed form key to be more specific
        with st.form("add_employee_form_emp_page"):
            # Required Fields Section
            st.subheader("Required Information")
            col1, col2 = st.columns(2)

            with col1:
                staff_id = st.text_input("Staff ID", value=generate_staff_id(), disabled=True, key="staff_id_emp_page")
                email = st.text_input("Email *", key="email_emp_page")
                full_name = st.text_input("Full Name *", key="full_name_emp_page")
                department = st.text_input("Department *", key="department_emp_page")

            with col2:
                job_title = st.text_input("Job Title *", key="job_title_emp_page")
                annual_gross = st.number_input("Annual Gross Pay (₦) *", min_value=0.0, key="annual_gross_emp_page")
                account_number = st.text_input("Account Number *", key="account_number_emp_page")

            col3, col4 = st.columns(2)
            with col3:
                contract_type = st.selectbox("Contract Type *", ["Full Time", "Contract"], key="contract_type_emp_page")
                start_date = st.date_input("Start Date *", key="start_date_emp_page")

            with col4:
                end_date = st.date_input("End Date (Optional)", key="end_date_emp_page")
                rsa_pin = st.text_input("RSA PIN (Optional)", key="rsa_pin_emp_page")

            # Optional Fields Section
            st.markdown("---")
            st.subheader("Optional Details")
            st.info("These fields can be updated later during payroll review.")

            col5, col6 = st.columns(2)
            with col5:
                reimbursements = st.number_input(
                    "Reimbursements (₦)",
                    min_value=0.0,
                    value=0.0,
                    help="Additional allowances like transport or meal allowances",
                    key="reimbursements_emp_page"
                )

            with col6:
                other_deductions = st.number_input(
                    "Other Deductions (₦)",
                    min_value=0.0,
                    value=0.0,
                    help="Additional deductions like loans or advances",
                    key="other_deductions_emp_page"
                )

            voluntary_pension = st.number_input(
                "Voluntary Pension (₦)",
                min_value=0.0,
                value=0.0,
                help="Additional voluntary pension contributions",
                key="voluntary_pension_emp_page"
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

    with tab2:
        st.subheader("Employee List")
        employees = get_all_employees()
        if employees:
            # Convert to DataFrame
            df = pd.DataFrame(employees)

            # Add search functionality
            search_term = st.text_input("🔍 Search employees by name, department, or ID", key="employee_search")
            if search_term:
                mask = (
                    df['full_name'].str.contains(search_term, case=False, na=False) |
                    df['department'].str.contains(search_term, case=False, na=False) |
                    df['staff_id'].str.contains(search_term, case=False, na=False)
                )
                df = df[mask]

            # Style the display
            st.markdown("""
            <style>
            .delete-button {
                background-color: #ff4b4b;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.3rem;
                border: none;
                cursor: pointer;
            }
            .delete-button:hover {
                background-color: #ff0000;
            }
            </style>
            """, unsafe_allow_html=True)

            # Create metrics
            col_metrics = st.columns(3)
            with col_metrics[0]:
                st.metric("Total Employees", len(df))
            with col_metrics[1]:
                st.metric("Departments", len(df['department'].unique()))
            with col_metrics[2]:
                st.metric("Contract Types", len(df['contract_type'].unique()))

            # Create expandable sections for each department
            departments = sorted(df['department'].unique())
            for dept in departments:
                dept_df = df[df['department'] == dept]
                with st.expander(f"📁 {dept} ({len(dept_df)} employees)"):
                    # Create a clean display table
                    display_cols = ['staff_id', 'full_name', 'job_title', 'email', 'contract_type']
                    display_df = dept_df[display_cols].copy()

                    # Rename columns for better display
                    display_df.columns = ['Staff ID', 'Name', 'Position', 'Email', 'Contract Type']

                    # Display the table
                    st.dataframe(
                        display_df,
                        column_config={
                            "Staff ID": st.column_config.TextColumn("Staff ID", width="medium"),
                            "Name": st.column_config.TextColumn("Name", width="large"),
                            "Position": st.column_config.TextColumn("Position", width="large"),
                            "Email": st.column_config.TextColumn("Email", width="large"),
                            "Contract Type": st.column_config.TextColumn("Contract Type", width="medium"),
                        },
                        hide_index=True
                    )

                    # Add delete buttons with better styling
                    for idx, employee in dept_df.iterrows():
                        col1, col2 = st.columns([4, 1])
                        with col2:
                            if st.button(
                                "🗑️ Delete Employee",
                                key=f"delete_{employee['id']}",
                                type="primary",
                                help=f"Delete {employee['full_name']}"
                            ):
                                # Use a more prominent confirmation dialog
                                st.warning(
                                    f"""
                                    ⚠️ Confirm Deletion

                                    You are about to delete the following employee:
                                    - Name: {employee['full_name']}
                                    - Staff ID: {employee['staff_id']}
                                    - Department: {employee['department']}

                                    This action cannot be undone.
                                    """
                                )
                                col_confirm, col_cancel = st.columns(2)
                                with col_confirm:
                                    if st.button("✓ Confirm Delete", key=f"confirm_{employee['id']}", type="primary"):
                                        success, message = delete_employee(employee['id'])
                                        if success:
                                            st.success(f"✅ Successfully deleted {employee['full_name']}")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Error: {message}")
                                with col_cancel:
                                    if st.button("✗ Cancel", key=f"cancel_{employee['id']}"):
                                        st.rerun()
        else:
            st.info("👥 No employees found in the system. Add employees using the 'Add Employee' tab.")

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
                                st.rerun()

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")