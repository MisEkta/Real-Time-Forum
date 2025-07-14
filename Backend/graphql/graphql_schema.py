import strawberry
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from ..database.models import User as UserModel, Topic as TopicModel, Comment as CommentModel
from strawberry.types import Info
from ..database.database import get_db
from sqlalchemy.future import select
import heapq
from sqlalchemy import func
from ..redis.redis import RedisCache

@strawberry.type
class User:
    id: int
    name: str
    email: str
    profile_image: Optional[str] 
    created_at: Optional[datetime]

@strawberry.type
class User_Topics:
    count :int
    topics :List['Topic']

@strawberry.type
class Topic:
    id: int
    title: str
    content: str
    user_id: int

@strawberry.type
class Comment:
    id: int
    content: str
    user_id: int

@strawberry.type
class Trend:
    id: int
    title: str
    content:str
    count: int
    
    
    def __lt__(self, other):
        if not isinstance(other, Trend):
            return NotImplemented
        return self.count < other.count

    def __eq__(self, other):
        if not isinstance(other, Trend):
            return NotImplemented
        return self.count == other.count



def get_user_details(info: Info, username: str) -> User:
    with get_db() as db:
        result = db.execute(select(UserModel).where(UserModel.name == username))
        user = result.scalars().first()
        if user:
            return User(
                id=user.id,
                name=user.name,
                email=user.email,
                profile_image=user.profile_image,
                created_at=user.created_at,  
            )
        return None

def get_user_topics(info: Info, user_id: int) -> User_Topics:
    with get_db() as db:
        # Fetch the count of topics
        topic_count_result = db.execute(
            select(func.count(TopicModel.id)).where(TopicModel.user_id == user_id)
        )
        topic_count = topic_count_result.scalar()

        # Fetch the topic details
        topic_details_result = db.execute(
            select(TopicModel).where(TopicModel.user_id == user_id)
        )
        topics = topic_details_result.scalars().all()

        # Map the topics to the Topic type
        topic_details = [
            Topic(id=topic.id, title=topic.title, content=topic.content, user_id=topic.user_id)
            for topic in topics
        ]

        # Return a User object with count and topics
        return User_Topics(count=topic_count, topics=topic_details)
    

def get_topic(info: Info, prefix: str) -> List[Topic]:
    with get_db() as db:
        result = db.execute(
            select(TopicModel).where(TopicModel.title.like(f"{prefix}%"))
        )
        topics = result.scalars().all()
        return [
            Topic(id=topic.id, title=topic.title, content=topic.content, user_id=topic.user_id)
            for topic in topics
        ]
        
        
        
def get_comment(info: Info, topic_id: int) -> Comment:
    with get_db() as db:
        result = db.execute(select(CommentModel).where(CommentModel.topic_id == topic_id))
        comment = result.scalars().first()
        return Comment(id=comment.id, content=comment.content, user_id=comment.user_id)



def get_trending_topics(info: Info, limit: int=10) -> List[Trend]:
    cache = RedisCache()
    cache_key = f"trending_topics:{limit}"
    
    # Try to get from cache
    cached_trends = cache.get(cache_key)
    if cached_trends:
        return [
            Trend(
                id=trend["id"],
                title=trend["title"],
                content=trend["content"],
                count=trend["count"]
            )
            for trend in cached_trends
        ]
    
    # If not in cache, query database
    with get_db() as db:
        trending_query = db.execute(
            select(
                TopicModel.id, 
                TopicModel.title, 
                TopicModel.content,
                func.count(CommentModel.id).label('comment_count') #group and aggregate
            )
            .outerjoin(CommentModel, TopicModel.id == CommentModel.topic_id)  #join tables (outer join)
            .group_by(TopicModel.id, TopicModel.title, TopicModel.content)
            .order_by(func.count(CommentModel.id).desc())  #order by comment count in descending order
            .limit(limit)
        )
        
        # Create trending topics list directly from query results
        trending = [
            Trend(
                id=topic_id,
                title=title,
                content=content,
                count=comment_count
            )
            for topic_id, title, content, comment_count in trending_query.all()
        ]
        
        # Cache the results
        cache.set(cache_key, [
            {
                "id": trend.id,
                "title": trend.title,
                "content": trend.content,
                "count": trend.count
            }
            for trend in trending
        ])
        
        return trending

@strawberry.type
class Query:
    user: User = strawberry.field(resolver=get_user_details)
    userTopics: User_Topics = strawberry.field(resolver=get_user_topics)
    topic: List[Topic] = strawberry.field(resolver=get_topic)
    comment: Comment = strawberry.field(resolver=get_comment)
    trend: List[Trend] = strawberry.field(resolver=get_trending_topics)

schema = strawberry.Schema(query=Query)