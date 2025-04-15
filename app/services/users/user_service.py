from fastapi import HTTPException, status
from app.repositories import UserRepository
from app.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from app.core import verify_password, get_password_hash, create_access_token, verify_token
import hashlib

class UserService:
    @staticmethod
    async def create_user(user_create: UserCreate ) -> UserResponse:
        user_create.password = hashlib.sha256(user_create.password.encode()).hexdigest()
        user = await UserRepository.create_user(user_create.dict())
        return UserResponse.from_orm(user)
    
    @staticmethod
    async def login_user(login: LoginRequest) -> LoginResponse:
        user = await UserRepository.get_user_by_email(login.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verifica si las contraseñas coinciden
        hashed_password = hashlib.sha256(login.password.encode()).hexdigest()
        if user.password != hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        # Generar el token JWT
        access_token = create_access_token(data={"sub": user.email})  # 'sub' es generalmente el identificador del usuario
        return LoginResponse(access_token=access_token, token_type="bearer")
     