"""
Notification components for the Nigerian Payroll System
"""

import streamlit as st
from sidebar_icons import get_icon_html

def success_message(message, auto_dismiss=True):
    """
    Display a success notification
    
    Args:
        message (str): Message to display
        auto_dismiss (bool, optional): Whether to auto-dismiss after 5 seconds
    """
    if auto_dismiss:
        html = f"""
        <div id="success-notification" class="notification notification-success">
            {get_icon_html("success")}
            <div>{message}</div>
        </div>
        <script>
            setTimeout(function() {{
                document.getElementById('success-notification').style.display = 'none';
            }}, 5000);
        </script>
        """
    else:
        html = f"""
        <div class="notification notification-success">
            {get_icon_html("success")}
            <div>{message}</div>
        </div>
        """
    
    st.markdown(html, unsafe_allow_html=True)

def error_message(message):
    """
    Display an error notification
    
    Args:
        message (str): Message to display
    """
    html = f"""
    <div class="notification notification-error">
        {get_icon_html("error")}
        <div>{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def warning_message(message):
    """
    Display a warning notification
    
    Args:
        message (str): Message to display
    """
    html = f"""
    <div class="notification notification-warning">
        {get_icon_html("warning")}
        <div>{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def info_message(message):
    """
    Display an info notification
    
    Args:
        message (str): Message to display
    """
    html = f"""
    <div class="notification notification-info">
        {get_icon_html("info")}
        <div>{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def loading_spinner(message="Loading..."):
    """
    Display a loading spinner
    
    Args:
        message (str, optional): Message to display with the spinner
    """
    with st.spinner(message):
        pass
        
def progress_bar(progress, label=None):
    """
    Display a styled progress bar
    
    Args:
        progress (float): Progress value between 0 and 1
        label (str, optional): Optional label for the progress bar
    """
    if label:
        st.markdown(f"<div class='text-helper'>{label}</div>", unsafe_allow_html=True)
        
    html = f"""
    <div class="progress-bar">
        <div class="progress-bar-value" style="width: {progress * 100}%;"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def step_indicator(steps, current_step):
    """
    Display a step indicator for multi-step processes
    
    Args:
        steps (list): List of step titles
        current_step (int): Index of the current step (0-based)
    """
    html = """<div class="step-indicator">"""
    
    for i, step_title in enumerate(steps):
        step_class = "step"
        if i < current_step:
            step_class += " completed"
        elif i == current_step:
            step_class += " active"
            
        html += f"""
        <div class="{step_class}">
            <div class="step-number">{i+1}</div>
            <div class="step-title">{step_title}</div>
            <div class="step-line"></div>
        </div>
        """
    
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def workflow_buttons(back_label="Back", next_label="Next", show_back=True, back_key=None, next_key=None):
    """
    Display consistent workflow navigation buttons
    
    Args:
        back_label (str): Label for the back button
        next_label (str): Label for the next button
        show_back (bool): Whether to show the back button
        back_key (str, optional): Key for the back button
        next_key (str, optional): Key for the next button
        
    Returns:
        tuple: (next_clicked, back_clicked) - boolean values indicating button clicks
    """
    html = """<div class="workflow-actions">"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if show_back:
            back_clicked = st.button(back_label, key=back_key, use_container_width=True)
        else:
            st.write("")
            back_clicked = False
    
    with col2:
        next_clicked = st.button(next_label, key=next_key, use_container_width=True)
        
    return next_clicked, back_clicked