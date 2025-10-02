from fastapi import FastAPI
from app.database import init_db, close_db
from app.api import photo_router, detection_router, auth_router, fields_router, reports_router
from app.core import settings

  

async def lifespan(app: FastAPI):

    try:
        await init_db()
        yield
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        await close_db()
     
    
app = FastAPI(
    title="MinaScan - Sistema de Detección de Plagas Agrícolas",
    version="1.0.0",
    description="""
    ## Sistema completo de detección de plagas agrícolas con autenticación JWT
    
    ### 🔐 Autenticación y Autorización
    - **JWT (JSON Web Tokens)** para autenticación segura
    - **Roles de usuario**: Empleado y Jefe
    - **Cifrado de datos sensibles** (teléfono, dirección, coordenadas, notas)
    - **Sistema de códigos únicos** para vincular empleados con jefes
    
    ### 👥 Gestión de Usuarios
    - **Jefe**: Puede tener múltiples empleados, generar códigos de vinculación, ver reportes de empleados
    - **Empleado**: Puede realizar inspecciones, generar reportes, vincularse a un jefe
    - **Relación uno a muchos**: Un jefe puede tener varios empleados, un empleado solo un jefe
    
    ### 🌾 Gestión de Campos
    - **Registro de campos** con tamaño en hectáreas
    - **Coordenadas GPS cifradas** para ubicación precisa
    - **Descripción detallada** de cada campo
    
    ### 🔍 Detección de Plagas
    - **Detección automática** usando Roboflow
    - **Coordenadas GPS** de la detección
    - **Porcentaje de campo afectado** por plaga
    - **Notas adicionales** cifradas
    - **Historial completo** de detecciones por usuario
    
    ### 📊 Reportes con IA
    - **Generación automática** usando Gemini AI
    - **Análisis técnico** de la situación
    - **Recomendaciones** basadas en datos
    - **Exportación a PDF** con formato profesional
    
    ### 🔒 Seguridad
    - **Cifrado de datos sensibles** en base de datos
    - **JWT con expiración** configurable
    - **Validación de roles** en cada endpoint
    - **Verificación de propiedad** de recursos
    """,
    contact={
        "name": "Equipo de Desarrollo MinaScan",
        "email": "soporte@minascan.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)


app.include_router(photo_router, prefix="/photo", tags=["📸 Imágenes"])
app.include_router(detection_router, prefix="/detection", tags=["🔍 Detección de Plagas"])
app.include_router(auth_router, prefix="/auth", tags=["🔐 Autenticación"])
app.include_router(fields_router, prefix="/fields", tags=["🌾 Gestión de Campos"])
app.include_router(reports_router, prefix="/reports", tags=["📊 Reportes con IA"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True)