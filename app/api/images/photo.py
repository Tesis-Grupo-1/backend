from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services import ImageService
from app.schemas import ImageUploadResponse
import logging

logger = logging.getLogger(__name__)


router = APIRouter()

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/jpg"]

@router.post("/upload", response_model=ImageUploadResponse,
             summary="Subir imagen",
             description="Sube una imagen al sistema y la almacena en AWS S3.",
             responses={
                 200: {"description": "Imagen subida exitosamente"},
                 400: {"description": "Tipo de archivo no permitido"},
                 500: {"description": "Error al subir la imagen"}
             })
async def upload_image(file: UploadFile = File(...), porcentaje_plaga: float = Form(0.0)):
    """
    Sube una imagen al sistema y la almacena en AWS S3.
    
    - **file**: Archivo de imagen (JPG, JPEG, PNG) - Requerido
    - **porcentaje_plaga**: Porcentaje de plaga asociado a la imagen (opcional, por defecto 0.0)
    
    **Tipos de archivo soportados:**
    - JPEG (.jpg, .jpeg)
    - PNG (.png)
    
    **Respuesta incluye:**
    - ID de la imagen subida
    - URL de la imagen en S3
    - Nombre del archivo
    - Fecha de subida
    
    **Límites:**
    - Tamaño máximo recomendado: 10MB
    - Formatos soportados: JPG, JPEG, PNG
    """
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.error(f"Tipo de archivo no permitido: {file.content_type}")
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Solo se permiten imágenes JPEG, PNG o JPG.")
    
    print(f"FORM DATA: file={file.filename}, porcentaje_plaga={porcentaje_plaga}")

    try:
        # Subir la imagen usando el servicio ImageService
        new_image = await ImageService.upload_image(file, porcentaje_plaga=porcentaje_plaga)  # Aquí puedes ajustar el porcentaje de plaga según sea necesario
        return new_image
    except Exception as e:
        # En caso de error, capturamos la excepción y respondemos con un error HTTP
        logger.error(f"Error al subir la imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")