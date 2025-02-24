
import streamlit as st
import pandas as pd
from typing import Dict, Optional
import logging
from pathlib import Path
from salary_calculator import SalaryCalculator
from utils import CSVValidator
from config import DEFAULT_COMPONENTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='streamlit_app.log'
)
logger = logging.getLogger(__name__)

class SalaryApp:
    """Main Streamlit application for salary calculations."""

    def __init__(self):
        self.setup_page_config()
        self.load_css()
        self.initialize_session_state()
        self.validator = CSVValidator()

    def setup_page_config(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Salary Calculation System",
            page_icon="💰",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def load_css(self) -> None:
        """Load custom CSS styles."""
        css_path = Path('styles.css')
        if css_path.exists():
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        else:
            logger.warning("styles.css not found")

    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'calculated_results' not in st.session_state:
            st.session_state.calculated_results = None
        if 'components' not in st.session_state:
            st.session_state.components = DEFAULT_COMPONENTS.copy()

    def render_sidebar(self) -> Dict[str, float]:
        """Render sidebar with salary component configuration."""
        st.sidebar.header("Salary Component Configuration")

        components = {}
        for component, default_value in DEFAULT_COMPONENTS.items():
            components[component] = st.sidebar.number_input(
                f"{component} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.components.get(component, default_value)),
                step=0.1,
                key=f"component_{component}"
            )

        total_percentage = sum(components.values())
        st.sidebar.metric(
            "Total Percentage",
            f"{total_percentage:.1f}%",
            delta=f"{100 - total_percentage:.1f}% remaining" if total_percentage != 100 else None
        )

        if total_percentage != 100:
            st.sidebar.error("Total percentage must equal 100%")
            return None

        return components

    def render_upload_section(self) -> Optional[pd.DataFrame]:
        """Render file upload section and handle CSV upload."""
        st.subheader("Upload Employee Data")

        # Template download
        template_data = self.validator.generate_csv_template()
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
            help="Upload your completed CSV file with employee data"
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                validation_result = self.validator.validate_csv(df)

                if validation_result['valid']:
                    st.success("File uploaded successfully!")
                    return df
                else:
                    st.error(f"Invalid CSV structure: {validation_result['message']}")
                    return None

            except Exception as e:
                logger.error(f"Error processing upload: {str(e)}")
                st.error(f"Error processing file: {str(e)}")
                return None

        return None

    def process_calculations(self, df: pd.DataFrame, components: Dict[str, float]) -> None:
        """Process salary calculations for uploaded data."""
        try:
            calculator = SalaryCalculator(components)
            results = calculator.process_dataframe(df)
            st.session_state.calculated_results = results

            st.subheader("Calculation Results")
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

            # Export results
            csv_data = results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Results CSV",
                data=csv_data,
                file_name="salary_calculations.csv",
                mime="text/csv"
            )

        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            st.error(f"Error during calculations: {str(e)}")

    def render_instructions(self) -> None:
        """Render help and instructions section."""
        with st.expander("How to Use"):
            st.markdown("""
            ### Quick Start Guide
            1. 📥 Download the CSV template
            2. 📝 Fill in your employee data
            3. ⚙️ Configure salary components in the sidebar
            4. 📤 Upload your completed CSV
            5. 🔄 Process calculations
            6. 💾 Download results

            ### Required CSV Columns
            - Account Number (Bank account)
            - STAFF ID (Unique identifier)
            - Email (Valid email address)
            - NAME (Full name)
            - DEPARTMENT
            - JOB TITLE
            - ANNUAL GROSS PAY (Yearly salary)
            - START DATE (YYYY-MM-DD)
            - END DATE (YYYY-MM-DD)
            - Contract Type ('Full Time' or 'Contract')
            - Reimbursements (Additional payments)
            - Other Deductions
            - VOLUNTARY_PENSION (Optional)

            ### Important Rules
            - Pension is calculated only for full-time employees
            - Minimum salary for pension: ₦30,000
            - Employee pension: 8% of pensionable earnings
            - Employer pension: 10% minimum
            - Voluntary pension cap: 1/3 of monthly salary
            - Pensionable earnings = Basic + Housing + Transport
            """)

    def run(self) -> None:
        """Run the Streamlit application."""
        try:
            st.title("Professional Salary Calculation System")

            components = self.render_sidebar()
            if not components:
                return

            uploaded_df = self.render_upload_section()
            if uploaded_df is not None:
                st.session_state.uploaded_data = uploaded_df
                st.subheader("Data Preview")
                st.dataframe(
                    uploaded_df,
                    use_container_width=True,
                    hide_index=True
                )

                if st.button("Calculate Salaries", type="primary"):
                    with st.spinner("Processing salaries..."):
                        self.process_calculations(uploaded_df, components)

            self.render_instructions()

        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            st.error(f"An unexpected error occurred: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    app = SalaryApp()
    app.run()
