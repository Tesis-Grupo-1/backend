from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services import DetectionService
from app.schemas import DetectionResponse
from PIL import Image, UnidentifiedImageError
import logging


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/save_detection")
async def save_detection(
    image_id: int = Form(...),
    result: str = Form(...),
    prediction_value: str = Form(...),
    time_initial: str = Form(...),
    time_final: str = Form(...),
    date_detection: str = Form(...),
):
    try:
        
        detection = await DetectionService.save_time(
            image_id=image_id,
            result=result,
            prediction_value=prediction_value,
            time_initial=time_initial,
            time_final=time_final,
            date_detection=date_detection
        )
        print(detection)
        return detection
    except ValueError as ve:
        logger.error(f"Formato inválido para campos de tiempo: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Formato inválido para hora: {str(ve)}")
    except Exception as e:
        logger.error(f"Error al guardar el tiempo de detección: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")