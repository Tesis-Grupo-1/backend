from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.field_service import FieldService
from app.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from app.models.user import User
from app.api.auth.auth import get_current_active_user, get_boss_user

router = APIRouter()

@router.post("/", response_model=FieldResponse,
             summary="Crear nuevo campo",
             description="Crea un nuevo campo agrícola para el usuario autenticado.",
             responses={
                 201: {"description": "Campo creado exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 422: {"description": "Datos de entrada inválidos"}
             })
async def create_field(
    field_data: FieldCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea un nuevo campo agrícola para el usuario autenticado.
    
    - **name**: Nombre del campo (requerido)
    - **size_hectares**: Tamaño del campo en hectáreas (requerido)
    - **location**: Coordenadas GPS del campo (requerido)
    - **description**: Descripción opcional del campo
    
    Las coordenadas y descripción se almacenan cifradas en la base de datos.
    """
    print(f"DATA: {field_data}")
    field = await FieldService.create_field(current_user.id, field_data)
    return FieldResponse.from_orm(field)

@router.get("/", response_model=List[FieldResponse],
            summary="Listar campos del usuario",
            description="Obtiene todos los campos del usuario autenticado.",
            responses={
                200: {"description": "Lista de campos obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"}
            })
async def get_fields(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene todos los campos del usuario autenticado.
    
    Retorna una lista con todos los campos registrados por el usuario.
    """
    fields = await FieldService.get_fields_by_user(current_user.id)
    return [FieldResponse.from_orm(field) for field in fields]

@router.get("/{field_id}", response_model=FieldResponse,
            summary="Obtener campo específico",
            description="Obtiene la información de un campo específico del usuario autenticado.",
            responses={
                200: {"description": "Campo obtenido exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Campo no encontrado"}
            })
async def get_field(
    field_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la información de un campo específico.
    
    - **field_id**: ID del campo a obtener
    """
    field = await FieldService.get_field_by_id(field_id, current_user.id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campo no encontrado"
        )
    return FieldResponse.from_orm(field)

@router.put("/{field_id}", response_model=FieldResponse,
            summary="Actualizar campo",
            description="Actualiza la información de un campo existente.",
            responses={
                200: {"description": "Campo actualizado exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Campo no encontrado"},
                422: {"description": "Datos de entrada inválidos"}
            })
async def update_field(
    field_id: int,
    field_data: FieldUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza la información de un campo existente.
    
    - **field_id**: ID del campo a actualizar
    - Todos los campos son opcionales en la actualización
    """
    field = await FieldService.update_field(field_id, current_user.id, field_data)
    return FieldResponse.from_orm(field)

@router.delete("/{field_id}",
               summary="Eliminar campo",
               description="Elimina un campo del usuario autenticado.",
               responses={
                   200: {"description": "Campo eliminado exitosamente"},
                   401: {"description": "Token JWT inválido o expirado"},
                   404: {"description": "Campo no encontrado"}
               })
async def delete_field(
    field_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina un campo del usuario autenticado.
    
    - **field_id**: ID del campo a eliminar
    
    ⚠️ **Advertencia**: Esta acción no se puede deshacer.
    """
    success = await FieldService.delete_field(field_id, current_user.id)
    return {"message": "Campo eliminado exitosamente"}

@router.get("/boss/employees", response_model=List[FieldResponse],
            summary="Listar campos de empleados",
            description="Obtiene todos los campos de los empleados vinculados al jefe autenticado.",
            responses={
                200: {"description": "Lista de campos de empleados obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                403: {"description": "Solo jefes pueden usar este endpoint"}
            })
async def get_employee_fields(current_user: User = Depends(get_boss_user)):
    """
    Obtiene todos los campos de los empleados vinculados al jefe autenticado.
    
    Solo los jefes pueden usar este endpoint.
    """
    fields = await FieldService.get_fields_by_boss(current_user.id)
    return [FieldResponse.from_orm(field) for field in fields]
