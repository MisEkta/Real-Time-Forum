# User profile page

import streamlit as st
from api.graphql import get_user_details
from api.auth import update_password, delete_user
from api.profile import update_profile_image

def render_profile_page():
    """
    Render the user profile page with account settings
    """
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .profile-container {
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .profile-header {
            color: #2E4053;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid #ECF0F1;
        }
        .profile-section {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .user-info {
            font-size: 16px;
            color: #34495E;
            line-height: 2;
        }
        .settings-header {
            color: #2C3E50;
            font-size: 20px;
            margin: 15px 0;
            padding-left: 10px;
            border-left: 4px solid #3498DB;
        }
        .danger-zone {
            background-color: #FFF5F5;
            border: 1px solid #FED7D7;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        div.stButton > button:first-child {
            background-color: #3498DB;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #2980B9;
            transform: translateY(-2px);
        }
        .profile-image-container {
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .profile-image-container img {
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #3498DB;
            transition: transform 0.3s ease;
        }
        .profile-image-container img:hover {
            transform: scale(1.05);
        }
        hr {
            margin: 20px 0;
            border: none;
            border-top: 1px solid #ECF0F1;
        }
        .settings-section {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state and check login
    if "email" not in st.session_state:
        st.session_state.email = "Email not available"
    
    if "user" not in st.session_state:
        st.warning("👋 Please login to view profile")
        return

    # Fetch user details
    user_details = get_user_details(st.session_state.user)
    if user_details:
        st.session_state.email = user_details.get("email", "Email not available")
        st.session_state.created_at = user_details.get("createdAt", "Date not available")
        st.session_state.profile_image = user_details.get("profileImage", "https://thumbs.dreamstime.com/b/default-avatar-profile-vector-user-profile-default-avatar-profile-vector-user-profile-profile-179376714.jpg?w=768")

    # Page header
    st.markdown('<h1 class="profile-header"> My Profile </h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown('<div class="profile-image-container">', unsafe_allow_html=True)
        profile_image = user_details.get("profileImage", "https://thumbs.dreamstime.com/b/default-avatar-profile-vector-user-profile-default-avatar-profile-vector-user-profile-profile-179376714.jpg?w=768")
        if profile_image:
            st.image(profile_image, width=150, caption="Profile Photo")
        else:
            st.image("https://thumbs.dreamstime.com/b/default-avatar-profile-vector-user-profile-default-avatar-profile-vector-user-profile-profile-179376714.jpg?w=768", width=150, caption="No Profile Photo")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown('<div class="user-info">', unsafe_allow_html=True)
        st.write(f"👤 **Username:** {st.session_state.user}")
        st.write(f"📧 **Email:** {st.session_state.email}")
        st.write(f"📅 **Member since:** {st.session_state.created_at}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Settings section
    with st.expander("⚙️ Account Settings"):
        # Add profile image update section
        st.markdown('<div class="settings-header">📷 Update Profile Photo</div>', unsafe_allow_html=True)
        with st.form("update_photo_form"):
            new_photo_url = st.text_input(
                label="Photo URL",
                placeholder="Enter URL of your profile photo (e.g., https://example.com/photo.jpg)",
                help="Enter a valid image URL"
            )
            
            col1, col2, col3 = st.columns([2,1,2])
            with col2:
                update_photo = st.form_submit_button("Update Photo")
            
            if update_photo:
                if not new_photo_url:
                    st.warning("⚠️ Please enter a photo URL")
                else:
                    if update_profile_image(st.session_state.token, new_photo_url):
                        st.success("✅ Profile photo updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile photo")

        # Password Update Section
        st.markdown('<div class="settings-header">🔐 Update Password</div>', unsafe_allow_html=True)
        with st.form("update_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            col1, col2, col3 = st.columns([2,1,2])
            with col2:
                update_password_submit = st.form_submit_button("Update")
            
            if update_password_submit:
                if not all([current_password, new_password, confirm_new_password]):
                    st.warning("⚠️ Please fill in all fields")
                elif new_password != confirm_new_password:
                    st.error("⚠️ New passwords do not match")
                elif update_password(password=current_password, new_password=new_password):
                    st.success("✅ Password updated successfully!")

        # Delete Account Section
        st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
        st.markdown('<div class="settings-header">⚠️ Delete Account</div>', unsafe_allow_html=True)
        st.warning("This action cannot be undone!")
        with st.form("delete_profile_form"):
            confirm_password = st.text_input("Confirm your password to delete profile", type="password")
            col1, col2, col3 = st.columns([2,1,2])
            with col2:
                delete_submit = st.form_submit_button("🗑️ Delete")
            
            if delete_submit:
                if not confirm_password:
                    st.error("⚠️ Please enter your password")
                elif delete_user(st.session_state.user, confirm_password):
                    st.success("✅ Profile deleted successfully!")
                    st.session_state.clear()
                    
        st.markdown('</div>', unsafe_allow_html=True)