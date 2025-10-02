from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
from app.core import settings
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate, UserResponse, UserLogin, Token, 
    LinkingCodeRequest, LinkingCodeResponse, UserUpdate
)
from app.models.user import User, UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = AuthService.verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = await User.get_or_none(email=email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtiene el usuario actual activo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

async def get_boss_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verifica que el usuario actual sea un jefe"""
    if current_user.role != UserRole.BOSS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de jefe"
        )
    return current_user

async def get_employee_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verifica que el usuario actual sea un empleado"""
    if current_user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de empleado"
        )
    return current_user

@router.post("/register", response_model=UserResponse, 
             summary="Registrar nuevo usuario",
             description="Crea una nueva cuenta de usuario en el sistema. Los jefes reciben automáticamente un código de vinculación.",
             responses={
                 201: {"description": "Usuario creado exitosamente"},
                 400: {"description": "Error de validación o usuario ya existe"},
                 422: {"description": "Datos de entrada inválidos"}
             })
async def register(user_data: UserCreate):
    """
    Registra un nuevo usuario en el sistema.
    
    - **email**: Email único (requerido)
    - **password**: Contraseña segura (requerido)
    - **full_name**: Nombre completo (requerido)
    - **role**: Rol del usuario (employee/boss) (requerido)
    
    Los jefes reciben automáticamente un código de vinculación para conectar empleados.
    """
    user = await AuthService.create_user(user_data)
    return UserResponse.from_orm(user)

@router.post("/login", response_model=Token,
             summary="Iniciar sesión",
             description="Autentica un usuario y devuelve un token JWT para acceder a los endpoints protegidos.",
             responses={
                 200: {"description": "Login exitoso"},
                 401: {"description": "Credenciales incorrectas"},
                 422: {"description": "Datos de entrada inválidos"}
             })
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Inicia sesión en el sistema y devuelve un token JWT.
    
    - **username**: Email del usuario (se usa el campo username del formulario para el email)
    - **password**: Contraseña
    
    El token JWT debe incluirse en el header 'Authorization: Bearer <token>' 
    para acceder a los endpoints protegidos.
    """
    user = await AuthService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse,
            summary="Obtener perfil del usuario",
            description="Obtiene la información del usuario autenticado actual.",
            responses={
                200: {"description": "Información del usuario obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"}
            })
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene la información del perfil del usuario autenticado.
    
    Requiere autenticación JWT válida.
    """
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse,
            summary="Actualizar perfil del usuario",
            description="Actualiza la información del perfil del usuario autenticado.",
            responses={
                200: {"description": "Perfil actualizado exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Usuario no encontrado"}
            })
async def update_user_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza la información del perfil del usuario autenticado.
    
    Todos los campos son opcionales. Solo se actualizarán los campos proporcionados.
    """
    updated_user = await AuthService.update_user(current_user.id, user_data)
    return UserResponse.from_orm(updated_user)

@router.post("/link-employee", response_model=LinkingCodeResponse,
             summary="Vincular empleado con jefe",
             description="Vincula un empleado a un jefe usando un código de vinculación único.",
             responses={
                 200: {"description": "Vinculación procesada (exitosa o fallida)"},
                 401: {"description": "Token JWT inválido o expirado"},
                 403: {"description": "Solo empleados pueden usar este endpoint"}
             })
async def link_employee(
    linking_data: LinkingCodeRequest,
    current_user: User = Depends(get_employee_user)
):
    """
    Vincula un empleado a un jefe usando un código de vinculación.
    
    - **linking_code**: Código de 8 caracteres proporcionado por el jefe
    
    Solo los empleados pueden usar este endpoint.
    """
    success = await AuthService.link_employee_to_boss(current_user.id, linking_data.linking_code)
    
    if success:
        # Obtener información del jefe
        boss = await AuthService.get_boss_by_employee(current_user.id)
        return LinkingCodeResponse(
            success=True,
            message="Empleado vinculado exitosamente",
            boss_name=boss.full_name if boss else None
        )
    else:
        return LinkingCodeResponse(
            success=False,
            message="Código de vinculación inválido"
        )

@router.get("/employees", response_model=List[UserResponse],
            summary="Listar empleados",
            description="Obtiene la lista de todos los empleados vinculados al jefe autenticado.",
            responses={
                200: {"description": "Lista de empleados obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                403: {"description": "Solo jefes pueden usar este endpoint"}
            })
async def get_employees(current_user: User = Depends(get_boss_user)):
    """
    Obtiene la lista de todos los empleados vinculados al jefe autenticado.
    
    Solo los jefes pueden usar este endpoint.
    """
    employees = await AuthService.get_employees_by_boss(current_user.id)
    return [UserResponse.from_orm(emp) for emp in employees]

@router.get("/boss", response_model=UserResponse,
            summary="Obtener información del jefe",
            description="Obtiene la información del jefe asignado al empleado autenticado.",
            responses={
                200: {"description": "Información del jefe obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                403: {"description": "Solo empleados pueden usar este endpoint"},
                404: {"description": "No tienes un jefe asignado"}
            })
async def get_boss(current_user: User = Depends(get_employee_user)):
    """
    Obtiene la información del jefe asignado al empleado autenticado.
    
    Solo los empleados pueden usar este endpoint.
    """
    boss = await AuthService.get_boss_by_employee(current_user.id)
    if not boss:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes un jefe asignado"
        )
    return UserResponse.from_orm(boss)

@router.post("/regenerate-linking-code",
             summary="Regenerar código de vinculación",
             description="Genera un nuevo código de vinculación para el jefe autenticado.",
             responses={
                 200: {"description": "Nuevo código generado exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 403: {"description": "Solo jefes pueden usar este endpoint"}
             })
async def regenerate_linking_code(current_user: User = Depends(get_boss_user)):
    """
    Genera un nuevo código de vinculación para el jefe autenticado.
    
    Solo los jefes pueden usar este endpoint.
    """
    new_code = await AuthService.regenerate_linking_code(current_user.id)
    return {"linking_code": new_code}

@router.get("/linking-code",
            summary="Obtener código de vinculación",
            description="Obtiene el código de vinculación actual del jefe autenticado.",
            responses={
                200: {"description": "Código de vinculación obtenido exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                403: {"description": "Solo jefes pueden usar este endpoint"},
                404: {"description": "No hay código de vinculación generado"}
            })
async def get_linking_code(current_user: User = Depends(get_boss_user)):
    """
    Obtiene el código de vinculación actual del jefe autenticado.
    
    Solo los jefes pueden usar este endpoint.
    """
    if not current_user.linking_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay código de vinculación generado"
        )
    return {"linking_code": current_user.linking_code}
