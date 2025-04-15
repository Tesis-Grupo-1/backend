from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from app.repositories import UserRepository
from app.services import UserService

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    existing_user = await UserRepository.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Crear el usuario
    new_user = await UserService.create_user(user)
    return new_user

@router.post("/login", response_model=LoginResponse)
async def login_user(login_request: LoginRequest):
    result = await UserService.login_user(login_request)
    return result
