from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .fastapi.api import router as api_router
from .fastapi.auth import router as auth_router
from .database.database import init_db
from .graphql.graphql_schema import schema
from strawberry.fastapi import GraphQLRouter
from .rabbitmq.rabbitmq import consume_messages
import threading

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()
    threading.Thread(target=notification_listener, daemon=True).start()

def notification_listener():
    def handle_message(message):
        print(f"Received message: {message}")
        # Implement logic to handle the message

    consume_messages("topic_queue", handle_message)
    consume_messages("user_queue", handle_message)
    

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
