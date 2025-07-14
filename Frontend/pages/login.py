# Login/register page

import streamlit as st
from api.auth import login, register


def render_login_page():
    """
    Render the login and registration page
    """
        
    st.title("Real-Time Forum - Login")
    
    # Initialize session states
    if 'registration_success' not in st.session_state:
        st.session_state.registration_success = False
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Login"
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    # Automatically select login tab after registration
    if st.session_state.registration_success:
        tab1.active = True
    
    # Custom CSS for both login and register forms
    st.markdown(
    """
    <style>
    .auth-form {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .form-header {
        color: #2E4053;
        font-size: 24px;
        margin-bottom: 20px;
        text-align: center;
    }
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        width: 100%;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    div.stMarkdown p {
        font-size: 14px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

    with tab1:
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### Welcome Back!")
            st.markdown("Please enter your credentials to log in.")
            
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if username and password:
                    if login(username, password):
                        st.success("Login successful! Redirecting...")
                        st.set_page_config(initial_state="expanded")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please try again.")
                else:
                    st.warning("Please enter both username and password.")
    
    with tab2:
        if st.session_state.registration_success:
            st.success("Registration successful!")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🔐 Proceed to Login"):
                    st.session_state.active_tab = "Login"
                    st.session_state.registration_success = False
                    st.rerun()
        
        with st.form("register_form"):
            st.markdown('<h3 class="form-header">Create Your Account</h3>', unsafe_allow_html=True)
            st.markdown("Join our community and start discussing!", help="Required fields are marked with *")
            
            col1, col2 = st.columns(2)
            with col1:
                reg_username = st.text_input("👤 Username*", placeholder="Choose a username")
            with col2:
                reg_email = st.text_input("📧 Email*", placeholder="Enter your email")
            
            reg_password = st.text_input("🔒 Password*", type="password", placeholder="Create a strong password")
            reg_confirm_password = st.text_input("🔒 Confirm Password*", type="password", placeholder="Repeat your password")
            
            st.markdown("---")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if reg_username and reg_email and reg_password:
                    if reg_password != reg_confirm_password:
                        st.error("⚠️ Passwords do not match")
                    else:
                        if register(reg_username, reg_email, reg_password):
                            st.success("✅ Registration successful!")
                            st.session_state.registration_success = True
                            st.balloons()
                            st.button("🔐 Go to Login", on_click=lambda: (
                                setattr(st.session_state, 'active_tab', 'Login'),
                                setattr(st.session_state, 'registration_success', False),
                                ))
                else:
                    st.warning("⚠️ Please fill in all required fields")