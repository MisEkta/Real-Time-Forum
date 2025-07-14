# Search page

import streamlit as st
from api.graphql import search_topics
from api.comments import add_comment

def render_search_page():
    """
    Render the search page for finding topics
    """
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .search-title {
            color: #2E4053;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 30px;
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #ECF0F1;
        }
        .search-box {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .result-card {
            background-color: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        .result-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .topic-title {
            color: #34495E;
            font-size: 20px;
            margin-bottom: 10px;
            font-weight: 500;
        }
        .topic-content {
            color: #666;
            font-size: 16px;
            line-height: 1.6;
        }
        .comment-section {
            background-color: #f8f9fa;
            border-left: 3px solid #3498DB;
            padding: 15px;
            margin-top: 15px;
            border-radius: 0 8px 8px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Page header
    st.markdown('<h1 class="search-title">🔍 Search Topics</h1>', unsafe_allow_html=True)

    # Search box
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            search_query = st.text_input("Search Topics", placeholder="Enter keywords to search topics...", label_visibility="collapsed")
        with col2:
            search_button = st.button("🔍 Search")
        st.markdown('</div>', unsafe_allow_html=True)

        if search_button:
            if search_query:
                with st.spinner('Searching...'):
                    search_results = search_topics(search_query)
                    st.session_state.search_results = search_results
            else:
                st.warning("⚠️ Please enter a search term")

    # Display search results
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        st.markdown(f'### 📚 Found {len(st.session_state.search_results)} results')
        for topic in st.session_state.search_results:
            with st.expander(f"📄 {topic['title']}", expanded=True):
                st.markdown(f'''
                    <div class="result-card">
                        <div class="topic-title">{topic['title']}</div>
                        <div class="topic-content">{topic['content']}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Comments section
                st.markdown('<div class="comment-section">', unsafe_allow_html=True)
                with st.form(key=f"search_comment_form_{topic['id']}"):
                    comment_content = st.text_area("💭 Add a comment", placeholder="Write your thoughts...")
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col2:
                        comment_submit = st.form_submit_button("💬 Comment")
                    
                    if comment_submit and comment_content:
                        with st.spinner('Posting comment...'):
                            if add_comment(topic['id'], comment_content):
                                st.success("✅ Comment posted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to post comment")
                st.markdown('</div>', unsafe_allow_html=True)
    elif search_query:
        st.info("👀 No results found. Try different keywords!")