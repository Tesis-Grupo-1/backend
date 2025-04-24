from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import ImageService
from app.schemas import ImageUploadResponse
import logging

logger = logging.getLogger(__name__)


router = APIRouter()

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/jpg"]

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.error(f"Tipo de archivo no permitido: {file.content_type}")
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Solo se permiten imágenes JPEG, PNG o JPG.")
    
    try:
        # Subir la imagen usando el servicio ImageService
        new_image = await ImageService.upload_image(file)
        return new_image
    except Exception as e:
        # En caso de error, capturamos la excepción y respondemos con un error HTTP
        logger.error(f"Error al subir la imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")