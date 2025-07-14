# forum_app/api/comments.py
# Comment-related API functions

import streamlit as st
import requests
from config import API_URL

def add_comment(topic_id, content):
    """
    Add a comment to a topic
    """
    try:
        response = requests.post(
            f"{API_URL}/comments/{topic_id}",
            json={"topic_id": topic_id, "content": content},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            st.success("Comment added successfully!")
            return True
        else:
            st.error(f"Failed to add comment: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error adding comment: {str(e)}")
        return False

def update_comment(comment_id, content):
    """
    Update an existing comment
    """
    try:
        response = requests.put(
            f"{API_URL}/comments/{comment_id}",
            params={"content": content},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            st.success("Comment updated successfully!")
            return True
        else:
            st.error(f"Failed to update comment: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error updating comment: {str(e)}")
        return False