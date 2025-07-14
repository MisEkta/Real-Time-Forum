# forum_app/utils/session.py
# Session state management

import streamlit as st

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'topics' not in st.session_state:
        st.session_state.topics = []
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []