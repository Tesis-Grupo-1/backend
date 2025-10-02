from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core import settings
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserUpdate
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera hash de la contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crea un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Autentica un usuario por email"""
        user = await User.get_or_none(email=email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """Crea un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = await User.get_or_none(email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
        
        # Generar código de vinculación si es jefe
        linking_code = None
        if user_data.role == UserRole.BOSS:
            linking_code = AuthService.generate_linking_code()
        
        # Crear usuario
        hashed_password = AuthService.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            linking_code=linking_code
        )
        await user.save()
        return user
    
    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdate) -> User:
        """Actualiza un usuario"""
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar campos
        for field, value in user_data.dict(exclude_unset=True).items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await user.save()
        return user
    
    @staticmethod
    async def link_employee_to_boss(employee_id: int, linking_code: str) -> bool:
        """Vincula un empleado a un jefe usando el código de vinculación"""
        # Buscar jefe por código
        boss = await User.get_or_none(linking_code=linking_code, role=UserRole.BOSS)
        if not boss:
            return False
        
        # Buscar empleado
        employee = await User.get_or_none(id=employee_id, role=UserRole.EMPLOYEE)
        if not employee:
            return False
        
        # Vincular
        employee.boss = boss
        await employee.save()
        return True
    
    @staticmethod
    async def get_employees_by_boss(boss_id: int) -> list[User]:
        """Obtiene todos los empleados de un jefe"""
        return await User.filter(boss_id=boss_id, role=UserRole.EMPLOYEE)
    
    @staticmethod
    async def get_boss_by_employee(employee_id: int) -> Optional[User]:
        """Obtiene el jefe de un empleado"""
        employee = await User.get_or_none(id=employee_id, role=UserRole.EMPLOYEE)
        if employee and employee.boss:
            return await User.get_or_none(id=employee.boss.id)
        return None
    
    @staticmethod
    def generate_linking_code() -> str:
        """Genera un código único de 8 caracteres para vincular empleados"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    @staticmethod
    async def regenerate_linking_code(user_id: int) -> str:
        """Regenera el código de vinculación para un jefe"""
        user = await User.get_or_none(id=user_id, role=UserRole.BOSS)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jefe no encontrado"
            )
        
        new_code = AuthService.generate_linking_code()
        user.linking_code = new_code
        await user.save()
        return new_code
