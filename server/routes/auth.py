from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from models.schemas import UserSignup, UserLogin, Token, UserResponse
from database import users_collection
from utils.auth import get_password_hash, verify_password, create_access_token, verify_token
from config import settings
from bson import ObjectId

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserSignup):
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create user in database
    user_data = {
        "name": user.name,
        "class_name": user.class_name,
        "email": user.email,
        "hashed_password": hashed_password
    }
    result = users_collection.insert_one(user_data)
    
    # Check if user was created
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User could not be created"
        )
    
    # Return user data
    return UserResponse(
        id=str(result.inserted_id),
        name=user.name,
        class_name=user.class_name,
        email=user.email
    )

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    # Find user by email
    db_user = users_collection.find_one({"email": user.email})
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(db_user["_id"])},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    # Get user from database
    user = users_collection.find_one({"_id": ObjectId(token_data["user_id"])})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        class_name=user["class_name"],
        email=user["email"]
    )
