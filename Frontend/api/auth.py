# Authentication API functions

import streamlit as st
import requests
from config import AUTH_URL

def login(username, password):
    """
    Login to the system with username and password
    """
    try:
        response = requests.post(
            f"{AUTH_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user = username
            st.session_state.current_page = 'home'
            st.rerun()  # Add rerun after successful login
            return True
        else:
            st.error("Invalid username or password")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def register(username, email, password):
    """
    Register a new user account
    """
    try:
        response = requests.post(
            f"{AUTH_URL}/register",
            json={"name": username, "email": email, "password": password, "grant_password": password}
        )
        if response.status_code == 200:
            st.success("Registration successful! Please login.")
            st.session_state.current_page = 'login'
            st.rerun()  # Add rerun after successful registration
            return True
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def update_password(password, new_password):
    """
    Update the current user's password
    """
    try:
        response = requests.put(
            f"{AUTH_URL}/update-password",
            params={"password": password, "new_password": new_password},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            st.success("Password updated successfully!")
            return True
        else:
            st.error(f"Password update failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Password update error: {str(e)}")
        return False

def logout():
    """
    Clear session state and log the user out
    """
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.current_page = 'login'
    st.session_state.notifications = []
    st.session_state.topics = []
    st.session_state.search_results = []

def delete_user(username: str, password: str) -> bool:
    """
    Delete a user account after password confirmation
    Args:
        username: The username of the account to delete
        password: Password confirmation
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add your API call implementation here
        response= requests.delete(
            f"{AUTH_URL}/delete-account/{id}",
            params={"password": password},
            json={"username": username, "password": password},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        return True
    except Exception as e:
        st.error(f"Error deleting profile: {str(e)}")
        return False