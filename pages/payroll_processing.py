import streamlit as st
import pandas as pd
from datetime import datetime
from database import (create_payroll_period, get_active_payroll_period, 
                     create_payroll_run, update_payroll_run_status)
from payslip_generator import PayslipGenerator

def render_payroll_processing():
    st.title("Payroll Processing")
    
    # Create tabs for different operations
    tab1, tab2 = st.tabs(["Process Payroll", "Review & Approve"])
    
    with tab1:
        render_process_payroll()
    
    with tab2:
        render_review_approve()

def render_process_payroll():
    st.subheader("Process Monthly Payroll")
    
    # Get or create payroll period
    active_period = get_active_payroll_period()
    
    if not active_period:
        st.warning("No active payroll period found. Please create one.")
        with st.form("create_period"):
            period_name = st.text_input("Period Name", value=f"Payroll {datetime.now().strftime('%B %Y')}")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if st.form_submit_button("Create Period"):
                success, message = create_payroll_period(
                    period_name,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info(f"Active Period: {active_period['period_name']}")
        if st.button("Process Payroll"):
            success, run_id = create_payroll_run(active_period['id'])
            if success:
                st.success(f"Payroll run created successfully. ID: {run_id}")
                st.info("Processing employee salaries...")
                # Here you would process salaries and generate payslips
                st.success("Payroll processing complete!")
            else:
                st.error(f"Failed to create payroll run: {run_id}")

def render_review_approve():
    st.subheader("Review and Approve Payroll")
    
    # Here you would implement the review and approval workflow
    st.info("Payroll review and approval feature coming soon!")
