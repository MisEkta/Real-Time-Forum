# Real-Time Forum Project 
<p>This is a Real-Time Forum application built using <b>FastAPI, GraphQL (Strawberry), Redis, RabbitMQ, and PostgreSQL</b>. 
<p>The application allows users to create topics, add comments, and receive notifications for activities related to their topics. It also includes a trending topics feature based on a scoring system.

## Features
- <b>User Authentication:</b> Secure user registration and login.
- <b>Topic Management:</b>Users can create, update, and delete topics.
- <b>Comment Management:</b> Users can add comments to topics.
- <b>Notifications:</b> Users receive notifications when someone comments on their topics.
- <b>Trending Topics:</b> Topics are ranked based on a scoring system (e.g., number of comments and topic age).
- <b>GraphQL Support:</b> Query topics, comments, and trending topics using GraphQL.
- <b>Real-Time Messaging:</b> RabbitMQ is used for event-driven notifications.
- <b>Redis Integration:</b> Redis is used for caching and session management.
- <b> Frontend Development: </b> Streamlit is used to create a basic frontend of the application.

## Technologies Used
- **Backend Framework:** FastAPI
- **Database:** PostgreSQL (running on Docker)
- **GraphQL:** Strawberry
- **Message Broker:** RabbitMQ (running on Docker)
- **Cache:**  (running on the system server)
- **ORM:** SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens)
- **Frontend:** Streamlit


## Project Structure
```
Real-Time Forum Project/
│
├── Backend/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py      # Database configuration and session management
│   │   └── models.py        # SQLAlchemy models
│   │
│   ├── fastapi/
│   │   ├── __init__.py
│   │   ├── api.py          # FastAPI routes and endpoints
│   │   ├── auth.py         # Authentication logic
│   │   └── operations.py   # CRUD operations
│   │
│   ├── graphql/
│   │   ├── __init__.py
│   │   └── graphql_schema.py # GraphQL schema definitions
│   │
│   ├── rabbitmq/
│   │   ├── __init__.py
│   │   └── rabbitmq.py     # RabbitMQ configuration and functions
│   │
│   ├── redis/
│   │   ├── __init__.py
│   │   └── redis.py  # Redis caching implementation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── structures.py    # Data structures (Trie, Heap)
│   │
│   ├── tests/
│   │   └── test_*.py       # Test files
│   │
│   └── main.py             # FastAPI application entry point
│
├── Frontend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication API calls
│   │   ├── comments.py     # Comment-related API calls
│   │   ├── graphql.py      # GraphQL queries
│   │   ├── profile.py      # Profile-related API calls
│   │   └── topics.py       # Topic-related API calls
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py         # Home page with trending topics
│   │   ├── login.py        # Login/Register page
│   │   ├── my_posts.py     # User's posts page
│   │   ├── notifications.py # Notifications page
│   │   ├── profile.py      # User profile page
│   │   └── search.py       # Search page
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── session.py      # Session state management
│   │
│   ├── config.py           # Frontend configuration
│   └── app.py             # Streamlit application entry point
│
├── docker-compose.yml      # Docker services configuration
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
└── README.md             # Project documentation
```

This structure shows:
- Backend services are organized by functionality
- Frontend components are separated into pages and API calls
- Clear separation of concerns between layers
- Modular architecture for easy maintenance
- Test files location and configuration
- Docker and deployment configurations


## Installation
### Prerequisites
- Python 3.10+
- Docker and Docker Compose
- PostgreSQL (via Docker)
- RabbitMQ (via Docker)
- Redis (installed on your system)

## Steps
### 1. Clone the Repository:
```sh
https://git.epam.com/ekta_mishra/real-time-forum
cd real-time-forum
```
### 2. Environment Setup:
- **Virtual Environment Setup**
```sh
python -m venv .virtualenvv
.virtualenvv\Scripts\activate  #on linux: source .virtualenvv/bin/activate
```
- **Docker Environment Setup**
```sh
# PostgreSQL Configuration
DATABASE_URL="postgresql://username:password@localhost/postgres"

# RabbitMQ Configuration
RABBITMQ_URL="amqp://username:password@localhost:5672/"

# Redis Configuration
REDIS_HOST="localhost"
REDIS_PORT=6379
```
### 3. Install Dependencies:
```sh
pip install -r requirements.txt
```
### 4. Set Up the Database:
- Update the database connection string in `database.py`.

### 5. Start RabbitMQ and PostgreSQL:

- Use Docker Compose to start RabbitMQ and PostgreSQL:
```sh
docker-compose up -d
```
### 6. Run the Application:
- **Backend**
```sh
uvicorn Backend.main:app --reload
```
- **Frontend**
```sh
streamlit run Frontend\app.py
```
### 7. Access the Application:
- **FastAPI Backend:** http://localhost:8000
- **FastAPI Docs:** http://127.0.0.1:8000/docs
- **GraphQL Playground:** http://127.0.0.1:8000/graphql
- **Streamlit Frontend:** http://localhost:8501

## REST API Endpoints


| **Method** | **Endpoint**        | **Description**     |
| ---------- | ------------        | ---------------     |
|    POST    | `/auth/register`    | Register a new user |
|POST|`/auth/login`|Login and get a JWT token|
|POST|`/api/topics`|Create a new topic|
|PUT|`/api/topics/{id}`|Update a topic|
|DELETE|`/api/topics/{id}/delete`|Delete a topic|
|POST|`/api/comments/{id}`|Add a comment to a topic|
|PUT|`/api/comments/{comment_id}`|Update a comment|
|GET|`/api/notifications`|Get unread notifications|
|GET|`/api/notifications/mark-read`|Mark notification as read|
|GET|`/api/notifications/all`|Get all notifications|
|PUT|`/api/users/update-profile-image`|Update user profile image|
|PUT|`/auth/update-password`|Update user password|
|DELETE|`/api/users/{user_id}`|Delete user account|

		
## GraphQL Queries
- ### Get User:
```
query GetUserDetails($username: String!) {
  user(username: $username) {
    id
    name
    email
    createdAt
    profileImage
  }
}
```
- ### Get Topic:
```
query GetTopics($prefix: String!) {
  topic(prefix: $prefix) {
    id
    title
    content
    userId
  }
}
```

- ### Get Trending Topics:
```
query GetTrendingTopics($limit: Int!) {
  trend(limit: $limit) {
    id
    title
    content
    count
  }
}
```

## Notifications
- Notifications are stored in the `notifications` table.
- Users receive notifications when someone comments on their topics.
- Example notification: `"User2 commented on your topic: How to learn Python"`


## Running Tests
- To run tests, use the following command:
```sh
pytest
```

## Additional Features
- Profile image management via URL
- Password update functionality
- Account deletion capability
- Notification management system
- Real-time topic search with prefix matching
- Topic commenting system
- User profile 

## Future Enhancements
- Add real-time WebSocket notifications.
- Implement user-to-user messaging.
- Add support for topic categories and tags.
- Improve the scoring system for trending topics.
