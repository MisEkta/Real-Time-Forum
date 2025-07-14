from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import List, Optional
import aiohttp
from .auth import get_current_user
from .operations import CRUDOperations, SearchOperations, TopicCreate, CommentCreate
from ..database.database import get_db
from ..database.models import User as Usermodel
# from ..utils.trending import get_trending_topics



app = FastAPI()
router = APIRouter()

class Topic(BaseModel):
    topic_id: int
    title: str
    content: str

class Comment(BaseModel):
    comment_id: int
    topic_id: int
    content: str

class User(BaseModel):
    user_name:str
    email:str
    password:str
    
class UserInDB(User):
    user_id:int
    hashed_password:str

# Add this model for the image URL
class ProfileImageUpdate(BaseModel):
    image_url: HttpUrl
    
@router.get("/forum")
def root():
    return {"message": "Welcome to the real time forum!"}

# Add topics
@router.post("/topics")
def create_topic(topic: TopicCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return CRUDOperations.create_topic(topic, db, current_user)

# Add comments
@router.post("/comments/{topic_id}")
def add_comment(topic_id: int, comment: CommentCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return CRUDOperations.add_comment(comment, db, current_user)

@router.get("/topics/{user_name}")
def get_topics_username(user_name: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    return SearchOperations.get_topics_username(user_name, db, current_user)





# Update topics
@router.put("/topics/{topic_id}")
def update_topic(topic_id: int, title: str, content: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    return CRUDOperations.update_topic(topic_id, title, content, db, current_user)

# Update comments
@router.put("/comments/{comment_id}")
def update_comment(comment_id: int, content: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    return CRUDOperations.update_comment(comment_id, content, db, current_user)


# Delete topics
@router.delete("/topics/{topic_id}/delete")
def delete_topic(topic_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    return CRUDOperations.delete_topic(topic_id, db, current_user)


# Delete user
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    return CRUDOperations.delete_user(user_id, db, current_user)



#notification functions:
#get unread notifications
@router.get("/notifications")
def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return SearchOperations.get_notifications(db, current_user)


#mark unread notifications as read
@router.get("/notifications/mark-read")
def mark_notifications_as_read(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return SearchOperations.mark_notification(db, current_user)


#get all notifications
@router.get("/notifications/all")
def get_all_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    retrieve all notifications for a user
    """
    return SearchOperations.get_all_notifications(db, current_user)



#Image upload function
# @router.post("/users/upload-profile-image")
# def upload_profile_image(
#     file: UploadFile = File(...),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     # Validate file type
#     if not file.content_type.startswith('image/'):
#         raise HTTPException(status_code=400, detail="File must be an image")
    
#     # Create unique filename
#     file_extension = os.path.splitext(file.filename)[1]
#     filename = f"user_{current_user.id}{file_extension}"
#     file_path = UPLOAD_DIR / filename
    
#     # Save file
#     with file_path.open("wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # Update database
#     image_url = f"/uploads/profile_images/{filename}"
#     db.query(Usermodel).filter(Usermodel.id == current_user.id).update(
#         {"profile_image": image_url}
#     )
#     db.commit()
    
#     return {"image_url": image_url}

async def validate_image_url(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                content_type = response.headers.get('content-type', '')
                return content_type.startswith('image/')
    except:
        return False

@router.put("/users/update-profile-image")
async def update_profile_image(
    image_data: ProfileImageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Update database with the provided URL
        db.query(Usermodel).filter(Usermodel.id == current_user.id).update(
            {"profile_image": str(image_data.image_url)}
        )
        db.commit()
        
        return {
            "message": "Profile image updated successfully",
            "image_url": str(image_data.image_url)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile image: {str(e)}"
        )

app.include_router(router)