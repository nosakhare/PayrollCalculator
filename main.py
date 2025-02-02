import streamlit as st
import pandas as pd
import numpy as np
from salary_calculator import SalaryCalculator
from utils import validate_csv, validate_percentages, generate_csv_template
import io

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

    # File upload section
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

    # Instructions
    with st.expander("How to Use"):
        st.markdown("""
        1. Download the CSV template using the button above
        2. Fill in the template with your employee data
        3. Configure salary component percentages in the sidebar
        4. Upload your completed CSV file
        5. Review the data preview
        6. Click 'Calculate Salaries' to process all employees
        7. Download the results

        **Required CSV Columns:**
        - Account Number
        - STAFF ID
        - Email
        - NAME
        - DEPARTMENT
        - JOB TITLE
        - ANNUAL GROSS PAY
        - START DATE
        - END DATE
        - Contract Type (must be 'Full Time' or 'Contract')
        - Reimbursements (additional payments/allowances)
        - Other Deductions (miscellaneous deductions)
        - VOLUNTARY_PENSION (Optional additional contribution)
        - EMPLOYER_PENSION_RATE (Minimum 10%)

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