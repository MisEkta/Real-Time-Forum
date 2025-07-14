# User's posts page

import streamlit as st
from api.topics import get_user_topics, update_topic, create_topic, delete_topic
from api.graphql import get_topic_comments

def render_my_posts_page():
    """
    Render the page showing all topics created by the current user
    """
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-title {
            color: #2E4053;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
            padding: 10px 0;
        }
        .topic-card {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .topic-title {
            color: #2C3E50;
            font-size: 20px;
            margin-bottom: 10px;
        }
        .topic-content {
            color: #34495E;
            font-size: 16px;
            line-height: 1.6;
        }
        .button-container {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .comment-section {
            background-color: #ffffff;
            border-left: 3px solid #3498DB;
            padding: 15px;
            margin-top: 15px;
        }
        .comment-box {
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
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
        </style>
    """, unsafe_allow_html=True)

    # Page header with create button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<h1 class="main-title">My Posts</h1>', unsafe_allow_html=True)
    with col2:
        if st.button("➕ New Post", help="Create new topic"):
            st.session_state.show_create_form = True

    # Create new topic form
    if 'show_create_form' in st.session_state and st.session_state.show_create_form:
        with st.form(key="create_topic_form"):
            st.subheader("Create New Post")
            new_title = st.text_input("Title", placeholder="Enter post title...")
            new_content = st.text_area("Content", placeholder="Write your post content...")
            col1, col2 = st.columns([4, 1])
            with col2:
                submit = st.form_submit_button("📝 Post")
            
            if submit:
                if new_title and new_content:
                    create_topic(title=new_title, content=new_content)
                    st.success("✅ Post created successfully")
                    st.session_state.show_create_form = False
                    st.rerun()
                else:
                    st.warning("⚠️ Please provide both title and content")

    # Fetch and display user's topics
    user_topics = get_user_topics(st.session_state.user)
    st.session_state.topics = user_topics

    if st.session_state.topics:
        for topic in st.session_state.topics:
            with st.expander(f"📄 {topic['title']}", expanded=True):
                st.markdown(f'<div class="topic-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="topic-content">{topic["content"]}</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([4, 0.5, 0.5])
                with col1:
                    with st.form(key=f"edit_topic_form_{topic['id']}"):
                        edit_title = st.text_input("Title", value=topic['title'])
                        edit_content = st.text_area("Content", value=topic['content'])
                        if st.form_submit_button("📝 Update"):
                            if edit_title and edit_content:
                                update_topic(topic['id'], edit_title, edit_content)
                                st.rerun()
                
                with col2:
                    if st.button("💬", key=f"comments_{topic['id']}", help="Show comments"):
                        st.session_state[f"show_comments_{topic['id']}"] = True
                        if f"topic_comments_{topic['id']}" not in st.session_state:
                            st.session_state[f"topic_comments_{topic['id']}"] = get_topic_comments(topic['id'])
                with col3:
                    if st.button("🗑️", key=f"delete_{topic['id']}", help="Delete post"):
                        if delete_topic(topic['id']):
                            st.success("✅ Post deleted")
                            st.rerun()

                # Comments section
                if st.session_state.get(f"show_comments_{topic['id']}", False):
                    st.markdown('<div class="comment-section">', unsafe_allow_html=True)
                    st.markdown("### 💬 Comments")
                    
                    comments = st.session_state.get(f"topic_comments_{topic['id']}", get_topic_comments(topic['id']))
                    
                    if comments:
                        for comment in comments:
                            st.markdown(f'''
                            <div class="comment-box">
                                <strong>@{comment['userId']}</strong><br>
                                {comment['content']}
                            </div>
                            ''', unsafe_allow_html=True)
                    else:
                        st.info("💭 No comments yet. Be the first to comment!")
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📝 You haven't created any posts yet. Click the '+' button to create your first post!")