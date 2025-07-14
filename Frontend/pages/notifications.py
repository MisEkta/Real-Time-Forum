# Notifications page

import streamlit as st
from api.topics import get_notifications, mark_notification_as_read, get_all_notifications

def render_notifications_page():
    """
    Render the notifications page showing all user notifications
    """
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .notifications-title {
            color: #2E4053;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
            padding: 10px 0;
        }
        .notification-card {
            background-color: #f8f9fa;
            border-left: 4px solid #3498DB;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .notification-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="notifications-title">Notifications</div>', unsafe_allow_html=True)
    
    with col2:
        # Initialize the toggle state in session state if it doesn't exist
        if 'show_all_notifications' not in st.session_state:
            st.session_state.show_all_notifications = False
        
        # Create a checkbox with a tick symbol
        show_all = st.checkbox("📋 Show all", value=st.session_state.show_all_notifications)
        
        # Update session state when checkbox changes
        if show_all != st.session_state.show_all_notifications:
            st.session_state.show_all_notifications = show_all
            
    if st.session_state.show_all_notifications:
        notifications = get_all_notifications()
        if not notifications:
            st.info("No notifications history")
            return  
    else:
        notifications = get_notifications()
        if not notifications:
            st.info("No notifications")
            return
    
    # Display notifications with conditional mark as read button
    for notification in notifications:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Different styling for read/unread notifications
            border_color = "#3498DB" if not notification.get('is_read') else "#95a5a6"
            st.markdown(f"""
                <div class="notification-card" style="border-left: 4px solid {border_color}">
                    <p>{notification['message']}</p>
                    <small>{notification['created_at']}</small>
                    <small style="color: #7f8c8d">{"✓ Read" if notification.get('is_read') else "• Unread"}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Only show mark as read button for unread notifications
            if not notification.get('is_read'):
                if st.button("Mark as read", key=f"mark_read_{notification['id']}"):
                    if mark_notification_as_read():
                        st.success("Marked as read")
                        st.rerun()