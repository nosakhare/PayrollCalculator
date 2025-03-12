import streamlit as st
import pandas as pd

def render_data_table(data, title=None):
    """Render a standardized data table with optional title"""
    if title:
        st.subheader(title)
    st.dataframe(pd.DataFrame(data))

def render_currency_input(label, key, min_value=0.0, help_text=None):
    """Render a standardized currency input field"""
    return st.number_input(
        f"{label} (₦)",
        min_value=min_value,
        value=0.0,
        help=help_text,
        key=key
    )

def render_date_range_selector(start_key="start_date", end_key="end_date"):
    """Render a standardized date range selector"""
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key=start_key)
    with col2:
        end_date = st.date_input("End Date", key=end_key)
    return start_date, end_date

def render_status_indicator(status, success_message, error_message):
    """Render a standardized status indicator"""
    if status:
        st.success(success_message)
    else:
        st.error(error_message)
