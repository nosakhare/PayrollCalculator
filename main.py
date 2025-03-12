import streamlit as st
from pages.employee_management import render_employee_management
from pages.salary_calculator_ui import render_salary_calculator
from pages.payroll_processing import render_payroll_processing
from database import init_db

# Must be the first Streamlit command
st.set_page_config(
    page_title="Nigerian Payroll System",
    page_icon="💰",
    layout="wide"
)

# Hide Streamlit's default menu and footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Create the sidebar navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page",
        ["Employee Management", "Salary Calculator", "Payroll Processing"]
    )

    if page == "Employee Management":
        render_employee_management()
    elif page == "Salary Calculator":
        render_salary_calculator()
    elif page == "Payroll Processing":
        render_payroll_processing()

if __name__ == "__main__":
    main()