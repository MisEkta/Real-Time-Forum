# Main application entry point

import streamlit as st
from utils.session import init_session_state
from pages.login import render_login_page
from pages.home import render_home_page
from pages.search import render_search_page
from pages.my_posts import render_my_posts_page
from pages.notifications import render_notifications_page
from pages.profile import render_profile_page
from api.auth import logout
from api.topics import get_notifications

# Add this at the start of your main.py or app.py
if 'show_create_form' not in st.session_state:
    st.session_state.show_create_form = False

def main():
    # Initialize session state
    init_session_state()
        
        
            
    # Create sidebar for navigation
    if st.session_state.token:
        # Add sidebar navigation
        st.sidebar.title(f"Welcome, {st.session_state.user}")
        st.sidebar.subheader("Navigation")
        
        # Navigation buttons
        if st.sidebar.button("🏠 Home"):
            st.session_state.current_page = 'home'
            st.rerun()
            
        if st.sidebar.button("🔍 Search Topics"):
            st.session_state.current_page = 'search'
            st.rerun()
            
        if st.sidebar.button("✒️ My Posts"):
            st.session_state.current_page = 'my_posts'
            st.rerun()
            
        # Notifications button with count
        notifications = get_notifications()
        notification_count = len(notifications)
        
        if notification_count > 0:
            if st.sidebar.button(f"🔔 Notifications ({notification_count})"):
                st.session_state.current_page = 'notifications'
                st.rerun()
        else:
            if st.sidebar.button("🔔 Notifications"):
                st.session_state.current_page = 'notifications'
                st.rerun()
            
        if st.sidebar.button("👤 Profile"):
            st.session_state.current_page = 'profile'
            st.rerun()
            
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()
    else:
        st.sidebar.empty()
        
        
        
    # Render the appropriate page
    if st.session_state.current_page == 'login':
        render_login_page()
    elif st.session_state.current_page == 'home':
        render_home_page()
    elif st.session_state.current_page == 'search':
        render_search_page()
    elif st.session_state.current_page == 'my_posts':
        render_my_posts_page()
    elif st.session_state.current_page == 'notifications':
        render_notifications_page()
    elif st.session_state.current_page == 'profile':
        render_profile_page()

if __name__ == "__main__":
    main()