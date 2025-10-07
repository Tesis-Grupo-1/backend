from typing import List, Optional
from fastapi import HTTPException, status
from app.models.field import Field
from app.models.user import User
from app.schemas.field import FieldCreate, FieldUpdate

class FieldService:
    
    @staticmethod
    async def create_field(user_id: int, field_data: FieldCreate) -> Field:
        """Crea un nuevo campo para un usuario"""
        # Verificar que el usuario existe
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado" 
            )
        
        # Crear campo
        # Nota: Asignamos location/description DESPUÉS de instanciar para asegurar
        # que se invoquen los property setters (cifrado) y evitar NULLs en DB.
        field = Field(
            name=field_data.name,
            size_hectares=field_data.size_hectares,
            cant_plants=field_data.cant_plants,
            user_id=user_id
        )

        # Dispara setters que cifran y escriben en _location/_description
        field.location = field_data.location
        field.description = field_data.description

        await field.save()
        return field
    
    @staticmethod
    async def get_fields_by_user(user_id: int) -> List[Field]:
        """Obtiene todos los campos de un usuario"""
        return await Field.filter(user_id=user_id)
    
    @staticmethod
    async def get_field_by_id(field_id: int, user_id: int) -> Optional[Field]:
        """Obtiene un campo específico de un usuario"""
        return await Field.get_or_none(id=field_id, user_id=user_id)
    
    @staticmethod
    async def update_field(field_id: int, user_id: int, field_data: FieldUpdate) -> Field:
        """Actualiza un campo"""
        field = await Field.get_or_none(id=field_id, user_id=user_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campo no encontrado"
            )
        
        # Actualizar campos
        for field_name, value in field_data.dict(exclude_unset=True).items():
            if hasattr(field, field_name):
                setattr(field, field_name, value)
        
        await field.save()
        return field
    
    @staticmethod
    async def delete_field(field_id: int, user_id: int) -> bool:
        """Elimina un campo"""
        field = await Field.get_or_none(id=field_id, user_id=user_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campo no encontrado"
            )
        
        await field.delete()
        return True
    
    @staticmethod
    async def get_fields_by_boss(boss_id: int) -> List[Field]:
        """Obtiene todos los campos de los empleados de un jefe"""
        # Obtener empleados del jefe
        employees = await User.filter(boss_id=boss_id, role="employee")
        employee_ids = [emp.id for emp in employees]
        
        # Obtener campos de los empleados
        return await Field.filter(user_id__in=employee_ids)
