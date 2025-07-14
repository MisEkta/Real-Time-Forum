from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from .auth import get_current_user
from ..database.models import User, Topic, Comment, Notification
from ..database.database import get_db
from ..rabbitmq.rabbitmq import publish_message
from ..utils.structures import Trie, Heap
from ..redis.redis import RedisCache

topic_trie = Trie()
topic_heap = Heap()
comment_trie = Trie()
comment_heap = Heap()

class TopicCreate(BaseModel):
    title: str
    content: str

class CommentCreate(BaseModel):
    topic_id: int
    content: str

class CRUDOperations:
    
    @staticmethod
    def create_topic(topic: TopicCreate, db: Session, current_user: User):
        new_topic = Topic(user_id=current_user.id, title=topic.title, content=topic.content)
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        publish_message("topic_queue", f"New topic created: {new_topic.title}")
        topic_trie.insert(new_topic.title)
        topic_heap.push((new_topic.id, new_topic.title))
        RedisCache().delete("trending_topics:*")  # Clear all trending caches
        return {"message": "Topic created"}

    @staticmethod
    def add_comment(comment: CommentCreate, db: Session, current_user: User):
        new_comment = Comment(user_id=current_user.id, topic_id=comment.topic_id, content=comment.content)
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        topic = db.execute(select(Topic).where(Topic.id == comment.topic_id)).scalars().first()
        if topic and topic.user_id != current_user.id:  # Avoid notifying the commenter themselves
            notification_message = f"{current_user.name} commented on your topic: {topic.title}"
            new_notification = Notification(user_id=topic.user_id, message=notification_message)
            db.add(new_notification)
            db.commit()
        publish_message(f'topic_queue', f'New Comment: {comment.content} for topic: {comment.topic_id}')
        comment_trie.insert(new_comment.content)
        comment_heap.push((new_comment.id, new_comment.content))
        RedisCache().delete("trending_topics:*")  # Clear all trending caches
        return {"message": "Comment added"}

    @staticmethod
    def update_topic(topic_id: int, title: str, content: str, db: Session, current_user: User):
        result = db.execute(select(Topic).where(Topic.id == topic_id).options(joinedload(Topic.owner)))
        topic = result.scalars().first()
        if not topic or topic.owner.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this topic")
        topic.title = title
        topic.content = content
        db.commit()
        publish_message("topic_queue", f"Topic updated: {topic.title}")
        topic_trie.insert(topic.title)
        topic_heap.push((topic.id, topic.title))
        return {"message": "Topic updated successfully"}

    @staticmethod
    def update_comment(comment_id: int, content: str, db: Session, current_user: User):
        result = db.execute(select(Comment).where(Comment.id == comment_id).options(joinedload(Comment.author)))
        comment = result.scalars().first()
        if not comment or comment.author.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this comment")
        comment.content = content
        db.commit()
        publish_message(f'topic_{comment.topic_id}', f"Comment updated: {comment.content}")
        comment_trie.insert(comment.content)
        comment_heap.push((comment.id, comment.content))
        return {"message": "Comment updated successfully"}
    
    @staticmethod
    def delete_topic(topic_id: int, db: Session, current_user: User):
        topic = db.execute(select(Topic).where(Topic.id == topic_id)).scalars().first()
        if not topic or topic.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not authorized to delete this topic"
            )
        
        try:
            # First delete all comments associated with the topic
            comments = db.execute(
                select(Comment).where(Comment.topic_id == topic_id)
            ).scalars().all()
            
            # Delete comments from database
            for comment in comments:
                db.delete(comment)
                
                # Remove from heap only (since Trie doesn't have remove)
                if hasattr(comment_heap, 'remove'):
                    try:
                        comment_heap.remove((comment.id, comment.content))
                    except ValueError:
                        pass  # Item not in heap
            
            # Delete the topic
            db.delete(topic)
            
            # Remove from heap only
            if hasattr(topic_heap, 'remove'):
                try:
                    topic_heap.remove((topic.id, topic.title))
                except ValueError:
                    pass  # Item not in heap
            
            db.commit()
            
            # Clear cache after successful deletion
            publish_message("topic_queue", f"Topic deleted: {topic.title}")
            RedisCache().delete("trending_topics:*")
            
            return {"message": "Topic deleted successfully"}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete topic: {str(e)}"
            )
    
    @staticmethod
    def delete_user(user_id: int, db: Session, current_user: User):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        
        
        Notifications = db.execute(select(Notification).where(Notification.user_id == user_id)).scalars().all()
        for notification in Notifications:
            db.delete(notification)
            
        
        comments = db.execute(select(Comment).where(Comment.user_id == user_id)).scalars().all()
        for comment in comments:
            db.delete(comment)
            comment_trie.remove(comment.content)
            comment_heap.remove((comment.id, comment.content))
        
        topics = db.execute(select(Topic).where(Topic.user_id == user_id)).scalars().all()
        for topic in topics:
            db.delete(topic)
            topic_trie.remove(topic.title)
            topic_heap.remove((topic.id, topic.title))
        
        user = db.execute(select(User).where(User.id == user_id)).scalars().first()
        if user:
            db.delete(user)
        
        db.commit()
        publish_message("user_queue", f"User deleted: {user_id}")
        return {"message": "User and related data deleted successfully"}
    
    
class SearchOperations:

    
    
    @staticmethod
    def get_topics_username(user_name: str, db: Session, current_user: User):
        result = db.execute(select(User).where(User.name.ilike(f'%{user_name}%')))
        user = result.scalars().first()
        if user:
            topics = db.execute(select(Topic).where(Topic.user_id == user.id)).scalars().all()
            return topics
        return []
    
    @staticmethod
    def search_topics(title: str, db: Session, current_user: User):
        if topic_trie.search(title):
            result = db.execute(select(Topic).where(Topic.title.ilike(f'%{title}%') | Topic.content.ilike(f'%{title}%')))
            topics = result.scalars().all()
            return topics
        return []
    
    @staticmethod
    def get_notifications(db: Session, current_user: User):
        # Fetch notifications for the current user, ordered by most recent first
        notifications = db.execute(
            select(Notification)
            .where(Notification.user_id == current_user.id)
            .where(Notification.is_read == False)
            .order_by(Notification.created_at.desc())
        ).scalars().all()
        
        # for notification in notifications:
        #     notification.is_read = True
            
        # db.commit()
        
        return [
            {
                "id": n.id, 
                "message": n.message, 
                "created_at": n.created_at
            } for n in notifications
        ]
    @staticmethod
    def mark_notification(db:Session, current_user: User):
        notifications = db.execute(
            select(Notification)
            .where(Notification.user_id == current_user.id)
            .where(Notification.is_read == False)
            .order_by(Notification.created_at.desc())
        ).scalars().all()
        
        for notification in notifications:
            notification.is_read = True
            
        db.commit()
        
        return [
            {
                "id": n.id, 
                "message": n.message, 
                "created_at": n.created_at,
                "is_read": n.is_read
            } for n in notifications
        ]
        
    @staticmethod
    def get_all_notifications(db: Session, current_user: User):
        # Fetch all notifications for the current user, ordered by most recent first
        notifications = db.execute(
            select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
        ).scalars().all()
        
        return [
            {
                "id": n.id, 
                "message": n.message, 
                "created_at": n.created_at,
                "is_read": n.is_read
            } for n in notifications
        ]