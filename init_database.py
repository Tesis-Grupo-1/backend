#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo.
Ejecutar: python init_database.py
"""

import asyncio
from app.database import init_db, close_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

async def create_sample_data():
    """Crea datos de ejemplo en la base de datos"""
    try:
        # Inicializar base de datos
        await init_db()
        
        # Crear jefe de ejemplo
        boss_data = UserCreate(
            email="jefe@ejemplo.com",
            password="password123",
            full_name="Juan Pérez",
            role=UserRole.BOSS
        )
        
        # Verificar si el jefe ya existe
        existing_boss = await User.get_or_none(email=boss_data.email)
        if not existing_boss:
            boss = await AuthService.create_user(boss_data)
            print(f"Jefe creado: {boss.email} - Código de vinculación: {boss.linking_code}")
        else:
            print(f"Jefe ya existe: {existing_boss.email} - Código de vinculación: {existing_boss.linking_code}")
        
        # Crear empleado de ejemplo
        employee_data = UserCreate(
            email="empleado@ejemplo.com",
            password="password123",
            full_name="María García",
            role=UserRole.EMPLOYEE
        )
        
        # Verificar si el empleado ya existe
        existing_employee = await User.get_or_none(email=employee_data.email)
        if not existing_employee:
            employee = await AuthService.create_user(employee_data)
            print(f"Empleado creado: {employee.email}")
        else:
            print(f"Empleado ya existe: {existing_employee.email}")
        
        print("\nDatos de ejemplo creados exitosamente!")
        print("Puedes usar estos usuarios para probar el sistema:")
        print("Jefe: jefe@ejemplo.com / password123")
        print("Empleado: empleado@ejemplo.com / password123")
        
    except Exception as e:
        print(f"Error al crear datos de ejemplo: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
