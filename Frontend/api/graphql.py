# forum_app/api/graphql.py
# GraphQL client and queries

import streamlit as st
from gql import Client
from gql import gql as gql_query
from gql.transport.requests import RequestsHTTPTransport
from config import GRAPHQL_URL
from datetime import datetime


# Set up GraphQL client
transport = RequestsHTTPTransport(url=GRAPHQL_URL)
client = Client(transport=transport, fetch_schema_from_transport=True)

def search_topics(prefix):
    """
    Search for topics with a title matching the given prefix
    """
    try:
        query = gql_query("""
        query GetTopics($prefix: String!) {
          topic(prefix: $prefix) {
            id
            title
            content
            userId
          }
        }
        """)
        result = client.execute(query, variable_values={"prefix": prefix})
        return result["topic"]
    except Exception as e:
        st.error(f"Error searching topics: {str(e)}")
        return []

def get_trending_topics(limit=10):
    """
    Get the trending topics up to the specified limit
    """
    try:
        query = gql_query("""
        query GetTrendingTopics($limit: Int!) {
          trend(limit: $limit) {
            id
            title
            content
            count
          }
        }
        """)
        result = client.execute(query, variable_values={"limit": limit})
        return result["trend"]
    except Exception as e:
        st.error(f"Error fetching trending topics: {str(e)}")
        return []

def get_user_details(username: str) -> dict:
    """
    Fetch user details from GraphQL API
    """
    try:
        query = gql_query("""
        query GetUserDetails($username: String!) {
          user(username: $username) {
            id
            name
            email
            createdAt
            profileImage
          }
        }
        """)
        result = client.execute(query, variable_values={"username": username})
        return result.get("user", {})
    except Exception as e:
        st.error(f"Error fetching user details: {str(e)}")
        return {}

# def update_profile_image(username: str, image_url: str) -> bool:
#     """
#     Update user's profile image URL
#     """
#     try:
#         query = gql_query("""
#         mutation UpdateProfileImage($username: String!, $imageUrl: String!) {
#           updateProfileImage(username: $username, imageUrl: $imageUrl) {
#             success
#             message
#           }
#         }
#         """)
#         result = client.execute(
#             query,
#             variable_values={
#                 "username": username,
#                 "imageUrl": image_url
#             }
#         )
#         return result.get("updateProfileImage", {}).get("success", False)
#     except Exception as e:
#         st.error(f"Error updating profile image: {str(e)}")
#         return False

def get_topic_comments(topic_id: int) -> list:
    """
    Fetch comments for a specific topic using GraphQL
    """
    try:
        query = gql_query("""
        query getComment($topicId: Int!) {
          comment(topicId: $topicId) {
            id
            content
            userId
          }
        }
        """)
        result = client.execute(query, variable_values={"topicId": topic_id})
        comment = result.get("comment")
        if comment:
          return[comment]
        else:
          return []
      
    except Exception as e:
        st.error(f"Error fetching comments: {str(e)}")
        return []



