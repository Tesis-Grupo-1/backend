from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services import DetectionService
from app.schemas import *
from PIL import Image, UnidentifiedImageError
import logging, cv2, base64, os
import numpy as np
from inference_sdk import InferenceHTTPClient
from datetime import datetime



router = APIRouter()

logger = logging.getLogger(__name__)

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="H5Uc16sKkVGtvQ5aIrFQ"  # Cambia por tu API key
)


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
        print("="*5 + "LOGS" + "="*5)
        print(DetectionResponse(idDetection=detection.id_detection, plaga=result, prediction_value=prediction_value))

        return DetectionResponse(idDetection=detection.id_detection, plaga=result, prediction_value=prediction_value)
    except ValueError as ve:
        logger.error(f"Formato inválido para campos de tiempo: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Formato inválido para hora: {str(ve)}")
    except Exception as e:
        logger.error(f"Error al guardar el tiempo de detección: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    

@router.post("/detect-pests", response_model=DetectionResponseBoxes)
async def detect_pests(
    file: UploadFile = File(...),
    return_image: bool = True
):
    """
    Detecta plagas en una imagen de hoja
    
    - **file**: Imagen de la hoja (JPG, PNG)
    - **return_image**: Si devolver la imagen con bounding boxes dibujados
    """
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Leer imagen
        contents = await file.read()
        
        # Convertir a imagen OpenCV
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="No se pudo procesar la imagen")
        
        img_height, img_width = image.shape[:2]
        
        # Guardar imagen temporalmente para Roboflow
        temp_filename = f"temp_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(temp_filename, image)
        
        try:
            # Ejecutar inferencia con Roboflow
            result = client.run_workflow(
                workspace_name="dl-w5fkx",
                workflow_id="detect-and-classify",
                images={"image": temp_filename},
                use_cache=True
            )
            
            # Procesar resultados
            first_result = result[0]
            detection_predictions = first_result["detection_predictions"]
            predictions = detection_predictions["predictions"]
            
            # Convertir predicciones a formato estándar
            detections = []
            for prediction in predictions:
                bbox = DetectionService.convert_roboflow_coordinates(prediction, img_width, img_height)
                detection = Detection(
                    class_name=prediction['class'],
                    confidence=prediction['confidence'],
                    bounding_box=bbox
                )
                detections.append(detection)
            
            # Dibujar bounding boxes si se solicita
            processed_image_base64 = None
            if return_image and detections:
                image_with_boxes = DetectionService.draw_bounding_boxes(image, detections)
                processed_image_base64 = DetectionService.image_to_base64(image_with_boxes)
            
            return DetectionResponseBoxes(
                success=True,
                message=f"Se detectaron {len(detections)} plagas",
                detections=detections,
                image_width=img_width,
                image_height=img_height,
                processed_image_base64=processed_image_base64
            )
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")
