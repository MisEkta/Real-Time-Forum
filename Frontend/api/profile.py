import requests
import streamlit as st
from config import API_URL

def update_profile_image(token: str, image_url: str) -> bool:
    """
    Update user's profile image using FastAPI endpoint
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "image_url": image_url
        }
        
        response = requests.put(
            f"{API_URL}/users/update-profile-image",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error: {response.json().get('detail', 'Failed to update profile image')}")
            return False
            
    except Exception as e:
        st.error(f"Error updating profile image: {str(e)}")
        return False