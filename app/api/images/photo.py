from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from app.services import ImageService
from app.schemas import ImageUploadResponse, DetectionImagesResponse, ImageResponse, ImageValidation
from app.models import User
import logging
from typing import List, Dict, Optional
from app.api.auth.auth import get_current_active_user


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
    

@router.get("/detection/{detection_id}", response_model=DetectionImagesResponse,
            summary="Obtener imágenes de una detección",
            description="Obtiene todas las imágenes asociadas a una detección específica",
            responses={
                200: {"description": "Imágenes obtenidas exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Detección no encontrada"}
            })
async def get_detection_images(
    detection_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todas las imágenes de una detección específica con sus estadísticas.
    
    - **detection_id**: ID de la detección
    
    Retorna:
    - Lista de imágenes con sus URLs y porcentajes de plaga
    - Estadísticas de validación
    - Cantidad de falsos positivos
    """
    return await ImageService.get_images_by_detection(detection_id, current_user.id)


@router.post("/validate/{image_id}", response_model=ImageResponse,
             summary="Validar una imagen",
             description="Permite al agricultor validar si una detección es correcta o un falso positivo",
             responses={
                 200: {"description": "Imagen validada exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 403: {"description": "No tienes permiso para validar esta imagen"},
                 404: {"description": "Imagen no encontrada"}
             })
async def validate_image(
    image_id: int,
    validation: ImageValidation,
    current_user: User = Depends(get_current_active_user)
):
    """
    Valida una imagen específica.
    
    - **image_id**: ID de la imagen a validar
    - **is_false_positive**: True si es un falso positivo, False si la detección es correcta
    
    Esta información se utiliza para mejorar el modelo de detección y calcular métricas de precisión.
    """
    image = await ImageService.validate_image(image_id, current_user.id, validation)
    return ImageResponse.from_orm(image)

@router.get("/stats/false-positives", response_model=Dict,
            summary="Estadísticas de falsos positivos",
            description="Obtiene estadísticas de falsos positivos del usuario",
            responses={
                200: {"description": "Estadísticas obtenidas exitosamente"},
                401: {"description": "Token JWT inválido o expirado"}
            })
async def get_false_positive_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas generales de falsos positivos del usuario.
    
    Retorna:
    - Total de imágenes validadas
    - Total de falsos positivos detectados
    - Tasa de falsos positivos (%)
    - Tasa de precisión del modelo (%)
    """
    return await ImageService.get_false_positive_stats(current_user.id)