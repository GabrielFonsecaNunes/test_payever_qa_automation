from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
import uvicorn 
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
    # Make the request to reqres.in
    response = httpx.get(f'https://reqres.in/api/users/{user_id}')
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve user from reqres.in")

    # Return the user
    return JSONResponse(content=response.json())

@app.delete('/api/user/{userId}')
def delete_user(user_id: int):
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

# Run the application using Uvicorn server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1:8000", port=8000)
