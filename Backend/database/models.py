from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    profile_image = Column(String(255), nullable=True)  # Add this line for image URL storage
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp for the user creation
    topics = relationship("Topic", back_populates="owner")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = 'topics'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp for the topic creation
    owner = relationship("User", back_populates="topics")
    comments = relationship("Comment", back_populates="topic")

class Comment(Base):
    __tablename__ = 'comments'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    content = Column(Text, nullable=False)
    author = relationship("User", back_populates="comments")
    topic = relationship("Topic", back_populates="comments")

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The user who will receive the notification
    message = Column(String, nullable=False)  # The notification message
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp for the notification
    is_read = Column(Boolean, default=False)  # Flag to indicate if the notification has

    user = relationship("User", back_populates="notifications")