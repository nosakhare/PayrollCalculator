"""
Authentication module for the Nigerian Payroll System
"""
import streamlit as st
from database import register_user, login_user, get_user_by_id
from notifications import success_message, error_message, info_message

def login_page():
    """Display the login page"""
    st.markdown("<h1 style='text-align: center;'>Nigerian Payroll System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please login to access your payroll dashboard</p>", unsafe_allow_html=True)
    
    # Add logo or image here if needed
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        
        # Create tabs for login and registration
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                st.subheader("Login")
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submit_button = st.form_submit_button("Login", use_container_width=True)
                
                if submit_button:
                    if not username or not password:
                        error_message("Please fill in all fields")
                    else:
                        success, result = login_user(username, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user = result
                            st.session_state.user_id = result['id']
                            success_message(f"Welcome back, {result['full_name']}!")
                            st.rerun()
                        else:
                            error_message(result)
        
        with tab2:
            with st.form("register_form", clear_on_submit=True):
                st.subheader("Create an Account")
                full_name = st.text_input("Full Name", key="reg_fullname")
                email = st.text_input("Email", key="reg_email")
                company_name = st.text_input("Company Name (Optional)", key="reg_company")
                username = st.text_input("Username", key="reg_username")
                password = st.text_input("Password", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
                
                submit_button = st.form_submit_button("Register", use_container_width=True)
                
                if submit_button:
                    # Validate inputs
                    if not full_name or not email or not username or not password or not confirm_password:
                        error_message("Please fill in all required fields")
                    elif password != confirm_password:
                        error_message("Passwords do not match")
                    elif len(password) < 6:
                        error_message("Password must be at least 6 characters long")
                    else:
                        success, result = register_user(username, email, password, full_name, company_name)
                        if success:
                            # Store the user ID in session state
                            st.session_state.logged_in = True
                            st.session_state.user_id = result
                            st.session_state.user = get_user_by_id(result)
                            success_message("Registration successful! You are now logged in.")
                            st.rerun()
                        else:
                            error_message(result)
        
        st.markdown("</div>", unsafe_allow_html=True)

def profile_page():
    """Display the user profile page"""
    if not st.session_state.get("user"):
        error_message("User information not available")
        return
    
    user = st.session_state.user
    
    st.title("My Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Full Name**: {user['full_name']}")
        st.markdown(f"**Username**: {user['username']}")
        st.markdown(f"**Email**: {user['email']}")
        if user.get('company_name'):
            st.markdown(f"**Company**: {user['company_name']}")
    
    with col2:
        st.markdown(f"**Account Created**: {user['created_at']}")
        
    if st.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.page = "Employee Management"  # Reset to default page
        success_message("You have been logged out")
        st.rerun()

def check_authentication():
    """Check if the user is authenticated"""
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    # Return True if logged in, False otherwise
    return st.session_state.get("logged_in", False)

def inject_custom_css():
    """Inject custom CSS for the authentication pages"""
    st.markdown("""
    <style>
    .login-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)