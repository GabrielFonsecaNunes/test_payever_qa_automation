from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
import json
import httpx

# Create the FastAPI app
app = FastAPI()

# Create the SQLite database engine
engine = create_engine('sqlite:///users.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the SQLAlchemy base model
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# API models
class CreateUserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

# API routes
@app.post('/api/users', response_model=UserResponse)
def create_user(user: CreateUserRequest):
    """
    Create a new user.

    Args:
        user: User data to create.

    Returns:
        Created user.

    Raises:
        HTTPException: If user with the same email already exists or failed to create user in reqres.in.
    """
    # Store the user entry in SQLite
    db = SessionLocal()
    db_user = User(name=user.name, email=user.email)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with the same email already exists")
    
    # Make the request to reqres.in
    response = httpx.post('https://reqres.in/api/users', json=user.dict())
    if response.status_code != 201:
        db.delete(db_user)
        db.commit()
        raise HTTPException(status_code=response.status_code, detail="Failed to create user in reqres.in")
    
    # Return the created user
    return JSONResponse(content=response.json())

@app.get('/api/user/{userId}', response_model=UserResponse)
def get_user(user_id: int):
    """
    Get user by ID.

    Args:
        user_id: ID of the user.

    Returns:
        Retrieved user.

    Raises:
        HTTPException: If failed to retrieve user from reqres.in.
    """
    # Make the request to reqres.in
    response = httpx.get(f'https://reqres.in/api/users/{user_id}')
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve user from reqres.in")

    # Return the user
    return JSONResponse(content=response.json())

@app.delete('/api/user/{userId}')
def delete_user(user_id: int):
    """
    Delete user by ID.

    Args:
        user_id: ID of the user.

    Returns:
        Success message.

    Raises:
        HTTPException: If user not found or failed to delete user from reqres.in.
    """
    # Delete the user entry from SQLite
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()

    # Make the request to reqres.in
    response = httpx.delete(f'https://reqres.in/api/users/{user_id}')
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail="Failed to delete user from reqres.in")
    
    # Return a success message
    return JSONResponse(content={"message": "User deleted successfully"})

# Get and delete users
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()

    # Get users with IDs 1, 2, 3
    for user_id in [1, 2, 3]:
        response = await get_user(user_id)
        user_data = json.loads(response.body)

        db_user = User(name=user_data["data"]["first_name"], email=user_data["data"]["email"])
        db.add(db_user)

    db.commit()

    # Delete user with ID 2
    await delete_user(2)

# Run the application using Uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.0", port=8000)