from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services import DetectionService
from app.schemas import DetectionResponse
from PIL import Image, UnidentifiedImageError
import logging


router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/predict")
async def predict(id_image: str = Form(...), file: UploadFile = File(...)) -> DetectionResponse:
    try:
        logger.info(f"Archivo recibido: {file.filename}")

        # Abrimos el archivo recibido directamente con PIL
        image = Image.open(file.file)

        # Preprocesar la imagen
        img_array = await DetectionService.preprocess_image(image)

        if img_array is None:
            raise ValueError("Error en el preprocesamiento de la imagen.")

        # Realizar la predicción
        prediction = await DetectionService.detect_plaga(img_array, id_image)

        logger.info({"prediction": prediction["prediction_value"], "plaga": prediction["plaga"], "class_label": prediction["class_label"]})

        return DetectionResponse(idDetection=prediction["idDetection"], plaga=prediction["plaga"], prediction_value=prediction["prediction_value"])

    except UnidentifiedImageError:
        logger.error("El archivo recibido no es una imagen válida.")
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida.")
    except ValueError as ve:
        logger.error(f"Error en el preprocesamiento de la imagen: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
@router.post("/save_detection_time")
async def save_detection_time(
    id_detection: int = Form(...),
    start_time2: str = Form(...),
    end_time2: str = Form(...),
    time_detection: float = Form(...)
):
    try:
        detection = await DetectionService.save_time(
            id_detection=id_detection,
            time_initial=start_time2,
            time_final=end_time2,
            time_detection=time_detection
        )
        return detection
    except Exception as e:
        logger.error(f"Error al guardar el tiempo de detección: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
