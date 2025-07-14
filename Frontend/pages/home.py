# forum_app/pages/home.py
# Home page with trending topics

import streamlit as st
from api.graphql import get_trending_topics
from api.topics import create_topic
from api.comments import add_comment

def render_home_page():
    """
    Render the home page with trending topics
    """
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-title {
            color: #2E4053;
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 30px;
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid #ECF0F1;
        }
        .section-title {
            color: #34495E;
            font-size: 18px;
            text-align: center;
            padding: 10px 0;
            margin: 20px 0;
            border-left: 4px solid #3498DB;
            padding-left: 10px;
        }
        .topic-card {
            background-color: #F8F9F9;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #E5E7E9;
        }
        .comment-section {
            background-color: #FFFFFF;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
        .create-topic-btn {
            background-color: #2ECC71;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .post-comment-btn {
            background-color: #3498DB;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # Welcome message with custom styling
    st.markdown(f'<h1 class="main-title">Welcome to Real-Time Forum, {st.session_state.user}! 👋</h1>', unsafe_allow_html=True)

    # Create new topic button at top
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("➕ New Topic", help="Create a new topic"):
            st.session_state.show_create_form = True

    # Create topic form
    if st.session_state.get('show_create_form', False):
        st.markdown('<div class="topic-card">', unsafe_allow_html=True)
        with st.form("new_topic_form"):
            st.subheader("Create New Topic")
            topic_title = st.text_input("Title")
            topic_content = st.text_area("Content")
            cols = st.columns([4, 1])
            with cols[1]:
                submit = st.form_submit_button("Post")
            
            if submit and topic_title and topic_content:
                if create_topic(topic_title, topic_content):
                    st.session_state.show_create_form = False
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Trending topics section
    st.markdown('<h2 class="section-title">Trending Topics</h2>', unsafe_allow_html=True)
    trending_topics = get_trending_topics(5)

    if trending_topics:
        for topic in trending_topics:
            st.markdown(f'''
                <div class="topic-card">
                    <h3>{topic['title']}</h3>
                    <p>{topic['content']}</p>
                    <small>💬 {topic['count']} comment count</small>
                </div>
            ''', unsafe_allow_html=True)

            # Comment section
            with st.expander("💭 Add Comment"):
                with st.form(key=f"comment_form_{topic['id']}"):
                    comment_content = st.text_area("Your comment")
                    cols = st.columns([4, 1])
                    with cols[1]:
                        comment_submit = st.form_submit_button("Post")
                    
                    if comment_submit and comment_content:
                        add_comment(topic['id'], comment_content)
                        st.rerun()
    else:
        st.info("👀 No trending topics yet. Be the first to create one!")