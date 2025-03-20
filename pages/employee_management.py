import streamlit as st
import pandas as pd
import time
from datetime import datetime
from database import add_employee, get_all_employees, generate_staff_id, delete_employee
from utils import validate_csv, process_bulk_upload, generate_csv_template

def render_page():
    # Get user ID from session state
    user_id = st.session_state.user_id
    
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
                staff_id = st.text_input("Staff ID", value=generate_staff_id(user_id), disabled=True, key="staff_id_emp_page")
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

                success, message = add_employee(employee_data, user_id)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with tab2:
        st.subheader("Employee List")
        employees = get_all_employees(user_id)
        if employees:
            # Convert to DataFrame
            df = pd.DataFrame(employees)

            # Add simple search
            search = st.text_input("🔍 Search by name or department")
            if search:
                df = df[
                    df['full_name'].str.contains(search, case=False, na=False) |
                    df['department'].str.contains(search, case=False, na=False)
                ]

            # Display employee table with key information
            display_cols = ['id', 'staff_id', 'full_name', 'department', 'job_title', 'contract_type']
            display_df = df[display_cols].copy()

            # Add View and Delete columns
            display_df['View'] = False
            display_df['Delete'] = False

            # Create metrics with data editor
            edited_df = st.data_editor(
                display_df,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                disabled=('id', 'staff_id', 'full_name', 'department', 'job_title', 'contract_type'),
                column_config={
                    "id": st.column_config.Column(
                        "ID",
                        help="Employee ID",
                        width="small",
                        required=True,
                        disabled=True
                    ),
                    "staff_id": st.column_config.Column(
                        "Staff ID",
                        help="Employee's unique identifier"
                    ),
                    "full_name": st.column_config.Column(
                        "Name",
                        help="Employee's full name"
                    ),
                    "department": st.column_config.Column(
                        "Department",
                        help="Employee's department"
                    ),
                    "job_title": st.column_config.Column(
                        "Position",
                        help="Employee's job title"
                    ),
                    "contract_type": st.column_config.Column(
                        "Contract Type",
                        help="Type of employment contract"
                    ),
                    "View": st.column_config.CheckboxColumn(
                        "View",
                        help="View employee details",
                        default=False,
                        required=True,
                        width="small"
                    ),
                    "Delete": st.column_config.CheckboxColumn(
                        "Delete",
                        help="Select employees to delete",
                        default=False,
                        required=True,
                        width="small"
                    )
                }
            )
            
            # Check if any employees are selected for viewing
            if edited_df['View'].any():
                selected_employee = edited_df[edited_df['View'] == True].iloc[0]
                st.query_params.id = selected_employee['id']
                st.query_params.page = "employee_details"
                st.rerun()

            # Check if any employees are selected for deletion
            has_selected = edited_df['Delete'].any()

            # Add custom styles for the delete button
            st.markdown("""
                <style>
                .stButton button {
                    width: 100%;
                }
                .delete-button button {
                    background-color: #ff4b4b;
                    color: white;
                    border: none;
                }
                .delete-button button:hover {
                    background-color: #ff3333;
                    color: white;
                    border: none;
                }
                .delete-button button:disabled {
                    background-color: #ffa6a6;
                    color: white;
                    border: none;
                    cursor: not-allowed;
                }
                </style>
            """, unsafe_allow_html=True)

            # Handle delete actions with a completely redesigned approach
            if has_selected:
                # Store selected employees in session state for persistence
                selected_employees = edited_df[edited_df['Delete'] == True]
                st.session_state.selected_employees_for_deletion = selected_employees
                
                # Display a notification showing selected employees
                st.warning(f"⚠️ {len(selected_employees)} employee(s) selected for deletion")
                
                # Show the selected employees
                st.subheader("Selected for deletion:")
                for _, row in selected_employees.iterrows():
                    st.info(f"{row['full_name']} ({row['staff_id']}) [ID: {row['id']}]")
                
                # Create a clear two-step process
                delete_col1, delete_col2 = st.columns(2)
                
                # Step 1: Initial deletion button (only shown when not in confirmation mode)
                if "confirm_delete_mode" not in st.session_state or not st.session_state.confirm_delete_mode:
                    if delete_col1.button("Delete Selected Employees", type="primary", key="trigger_delete_confirmation"):
                        st.session_state.confirm_delete_mode = True
                        st.rerun()
                
                # Step 2: Confirmation buttons (only shown in confirmation mode)
                if "confirm_delete_mode" in st.session_state and st.session_state.confirm_delete_mode:
                    st.error("⚠️ WARNING: This action cannot be undone!")
                    st.markdown("**Are you sure you want to delete these employees?**")
                    
                    # Cancel button
                    if delete_col1.button("Cancel", key="cancel_delete_action"):
                        # Reset confirmation mode
                        st.session_state.confirm_delete_mode = False
                        st.rerun()
                    
                    # Confirm button with a different color and more prominent
                    if delete_col2.button("Yes, Delete Permanently", type="primary", key="confirm_delete_action"):
                        # Process the deletion
                        success_count = 0
                        error_count = 0
                        error_messages = []
                        
                        # Get the employees from session state to ensure consistency
                        if "selected_employees_for_deletion" in st.session_state:
                            for _, row in st.session_state.selected_employees_for_deletion.iterrows():
                                # Process employee deletion
                                success, message = delete_employee(row['id'], user_id)
                                
                                if success:
                                    success_count += 1
                                else:
                                    error_count += 1
                                    error_messages.append(f"Failed to delete {row['full_name']}: {message}")
                        
                        # Reset confirmation mode
                        st.session_state.confirm_delete_mode = False
                        
                        # Show results
                        if success_count > 0:
                            st.session_state.delete_success_message = f"Successfully deleted {success_count} employee(s)"
                        
                        if error_count > 0:
                            st.session_state.delete_error_messages = error_messages
                        
                        # Rerun to refresh the page
                        st.rerun()
            
            # Display success message from previous operation if exists
            if "delete_success_message" in st.session_state:
                st.success(st.session_state.delete_success_message)
                # Remove the message after displaying once
                del st.session_state.delete_success_message
            
            # Display error messages from previous operation if they exist
            if "delete_error_messages" in st.session_state and st.session_state.delete_error_messages:
                for error_msg in st.session_state.delete_error_messages:
                    st.error(error_msg)
                # Remove the messages after displaying once
                del st.session_state.delete_error_messages

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
                            results = process_bulk_upload(df, user_id)

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