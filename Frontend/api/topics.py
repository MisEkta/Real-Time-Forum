# forum_app/api/topics.py
# Topic-related API functions

import streamlit as st
import requests
from config import API_URL

def create_topic(title, content):
    """
    Create a new topic
    """
    try:
        response = requests.post(
            f"{API_URL}/topics",
            json={"title": title, "content": content},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            st.success("Topic created successfully!")
            return True
        else:
            st.error(f"Failed to create topic: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error creating topic: {str(e)}")
        return False

def update_topic(topic_id, title, content):
    """
    Update an existing topic
    """
    try:
        response = requests.put(
            f"{API_URL}/topics/{topic_id}",
            params={"title": title, "content": content},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            st.success("Topic updated successfully!")
            return True
        else:
            st.error(f"Failed to update topic: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error updating topic: {str(e)}")
        return False

def get_user_topics(username):
    """
    Get all topics created by a specific user
    """
    try:
        response = requests.get(
            f"{API_URL}/topics/{username}",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch topics: {response.json().get('detail', 'Unknown error')}")
            return []
    except Exception as e:
        st.error(f"Error fetching topics: {str(e)}")
        return []

def get_notifications():
    """
    Get all unread notifications for the current user
    """
    try:
        response = requests.get(
            f"{API_URL}/notifications",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch notifications: {response.json().get('detail', 'Unknown error')}")
            return []
    except Exception as e:
        st.error(f"Error fetching notifications: {str(e)}")
        return []
    
def mark_notification_as_read():
    """
    Mark a notification as read
    """
    try:
        response = requests.get(
            f"{API_URL}/notifications/mark-read",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            st.success("Notification marked as read!")
            return True
        else:
            st.error(f"Failed to mark notification as read: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error marking notification as read: {str(e)}")
        return False


def get_all_notifications():
    """
    Get all notifications (both read and unread) for the current user
    """
    try:
        response = requests.get(
            f"{API_URL}/notifications/all",  # Note: Fix the missing slash in the API endpoint
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch all notifications: {response.json().get('detail', 'Unknown error')}")
            return []
    except Exception as e:
        st.error(f"Error fetching all notifications: {str(e)}")
        return []

def delete_topic(topic_id: str) -> bool:
    """
    Delete a topic from the database
    Args:
        topic_id: The ID of the topic to delete
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add your API call implementation here
        response = requests.delete(
            f"{API_URL}/topics/{topic_id}/delete",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        return True
    except Exception as e:
        st.error(f"Error deleting topic: {str(e)}")
        return False