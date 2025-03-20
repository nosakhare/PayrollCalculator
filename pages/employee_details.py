import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_employee_by_id, add_employee

def render_page():
    # Get user ID from session state
    user_id = st.session_state.user_id
    
    # Check if employee_id is in query parameters
    if not st.query_params.get("id"):
        st.warning("No employee selected. Please select an employee from the employee list.")
        st.stop()
    
    # Get employee ID from query parameters
    employee_id = int(st.query_params.id)
    
    # Fetch employee data
    employee = get_employee_by_id(employee_id, user_id)
    
    if not employee:
        st.error("Employee not found or you don't have permission to view this employee.")
        st.stop()
    
    # Display employee header
    st.subheader(f"{employee['full_name']} ({employee['staff_id']})")
    st.markdown(f"**Department:** {employee['department']} | **Position:** {employee['job_title']}")
    
    # Create tabs for viewing and editing
    view_tab, edit_tab = st.tabs(["View Details", "Edit Details"])
    
    with view_tab:
        display_employee_details(employee)
    
    with edit_tab:
        edit_employee_details(employee)

def display_employee_details(employee):
    """Display all employee details in a well-formatted view"""
    
    # Personal Information Section
    st.markdown("### Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Full Name:** {employee['full_name']}")
        st.info(f"**Staff ID:** {employee['staff_id']}")
        st.info(f"**Email:** {employee['email']}")
        
    with col2:
        st.info(f"**Department:** {employee['department']}")
        st.info(f"**Job Title:** {employee['job_title']}")
        st.info(f"**Contract Type:** {employee['contract_type']}")
    
    # Contract Information Section
    st.markdown("### Contract Information")
    col3, col4 = st.columns(2)
    
    with col3:
        st.info(f"**Annual Gross Pay:** ₦{employee['annual_gross_pay']:,.2f}")
        st.info(f"**Start Date:** {employee['start_date']}")
        if employee['end_date']:
            st.info(f"**End Date:** {employee['end_date']}")
    
    with col4:
        st.info(f"**Account Number:** {employee['account_number']}")
        if employee['rsa_pin']:
            st.info(f"**RSA PIN:** {employee['rsa_pin']}")
    
    # Additional Details Section
    st.markdown("### Additional Details")
    col5, col6 = st.columns(2)
    
    with col5:
        st.info(f"**Reimbursements:** ₦{employee['reimbursements']:,.2f}")
    
    with col6:
        st.info(f"**Other Deductions:** ₦{employee['other_deductions']:,.2f}")
        st.info(f"**Voluntary Pension:** ₦{employee['voluntary_pension']:,.2f}")
    
    # Back Button
    st.markdown("---")
    if st.button("← Back to Employee List"):
        # Navigate back to employee list
        st.query_params.clear()  # Clear parameters
        st.rerun()

def edit_employee_details(employee):
    """Provide form for editing employee details"""
    
    with st.form("edit_employee_form"):
        st.subheader("Edit Employee Information")
        
        # Required Fields Section
        st.markdown("### Required Information")
        col1, col2 = st.columns(2)
        
        with col1:
            staff_id = st.text_input("Staff ID", value=employee['staff_id'], disabled=True)
            email = st.text_input("Email *", value=employee['email'])
            full_name = st.text_input("Full Name *", value=employee['full_name'])
            department = st.text_input("Department *", value=employee['department'])
        
        with col2:
            job_title = st.text_input("Job Title *", value=employee['job_title'])
            annual_gross = st.number_input("Annual Gross Pay (₦) *", min_value=0.0, value=float(employee['annual_gross_pay']))
            account_number = st.text_input("Account Number *", value=employee['account_number'])
        
        col3, col4 = st.columns(2)
        with col3:
            contract_type = st.selectbox("Contract Type *", ["Full Time", "Contract"], index=0 if employee['contract_type'] == "Full Time" else 1)
            start_date = st.date_input("Start Date *", value=datetime.strptime(employee['start_date'], '%Y-%m-%d'))
        
        with col4:
            if employee['end_date']:
                end_date = st.date_input("End Date (Optional)", value=datetime.strptime(employee['end_date'], '%Y-%m-%d'))
            else:
                end_date = st.date_input("End Date (Optional)")
            rsa_pin = st.text_input("RSA PIN (Optional)", value=employee['rsa_pin'] if employee['rsa_pin'] else "")
        
        # Optional Fields Section
        st.markdown("---")
        st.subheader("Optional Details")
        st.info("These fields can be updated during payroll review as well.")
        
        col5, col6 = st.columns(2)
        with col5:
            reimbursements = st.number_input(
                "Reimbursements (₦)",
                min_value=0.0,
                value=float(employee['reimbursements']),
                help="Additional allowances like transport or meal allowances"
            )
        
        with col6:
            other_deductions = st.number_input(
                "Other Deductions (₦)",
                min_value=0.0,
                value=float(employee['other_deductions']),
                help="Additional deductions like loans or advances"
            )
        
        voluntary_pension = st.number_input(
            "Voluntary Pension (₦)",
            min_value=0.0,
            value=float(employee['voluntary_pension']),
            help="Additional voluntary pension contributions"
        )
        
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            if not email or not full_name or not department or not job_title or not annual_gross or not account_number:
                st.error("Please fill in all required fields marked with *")
                return
            
            # Prepare employee data for update
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
            
            # Update employee
            success, message = add_employee(employee_data, user_id)
            if success:
                st.success(message)
                # Refresh the page with updated data
                st.rerun()
            else:
                st.error(message)
    
    # Cancel button outside the form to return to the view tab
    if st.button("Cancel"):
        # Return to view tab
        st.rerun()