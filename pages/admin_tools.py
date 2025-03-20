import streamlit as st
import pandas as pd
from database import get_all_employees, delete_employee

def render_page():
    """Admin tools page for direct database operations"""
    
    # Get user ID from session state
    user_id = st.session_state.user_id
    
    st.title("Admin Tools")
    st.warning("These are administrative tools for direct database operations")
    
    with st.expander("Employee Management", expanded=True):
        st.subheader("Delete Employee")
        
        # Get all employees for this user
        employees = get_all_employees(user_id)
        
        if not employees:
            st.info("No employees found")
        else:
            # Convert to DataFrame for display
            df = pd.DataFrame(employees)
            st.dataframe(df[['id', 'staff_id', 'full_name', 'department']])
            
            # Direct employee deletion
            st.subheader("Delete Employee by ID")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                employee_id = st.number_input("Enter employee ID to delete", min_value=1, step=1)
            
            with col2:
                if st.button("Delete Now", type="primary"):
                    if employee_id:
                        # Confirm employee exists first
                        employee_exists = any(emp['id'] == employee_id for emp in employees)
                        
                        if not employee_exists:
                            st.error(f"No employee found with ID {employee_id}")
                        else:
                            with st.spinner("Deleting employee..."):
                                success, message = delete_employee(employee_id, user_id)
                                
                                if success:
                                    st.success(f"Successfully deleted employee with ID {employee_id}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete employee: {message}")
                    else:
                        st.error("Please enter an employee ID")