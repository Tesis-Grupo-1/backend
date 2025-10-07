from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from app.services import DetectionService
from app.schemas import DetectionCreate, DetectionUpdate, DetectionHistoryResponse, DetectionResponse, DetectionResponseBoxes
from app.models.user import User
from app.api.auth.auth import get_current_active_user, get_boss_user
from PIL import Image, UnidentifiedImageError
import logging, cv2, base64, os
import numpy as np
from inference_sdk import InferenceHTTPClient
from datetime import datetime
from typing import List



router = APIRouter()

logger = logging.getLogger(__name__)

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="H5Uc16sKkVGtvQ5aIrFQ"  # Cambia por tu API key
)


@router.post("/save_detection", response_model=DetectionResponse,
             summary="Guardar detección (Legacy)",
             description="Endpoint legacy para guardar detecciones. Se recomienda usar /create para nuevas implementaciones.",
             responses={
                 200: {"description": "Detección guardada exitosamente"},
                 422: {"description": "Formato inválido para campos de tiempo"},
                 500: {"description": "Error interno del servidor"}
             },
             deprecated=True)
async def save_detection(
    image_id: int = Form(...),
    result: str = Form(...),
    prediction_value: str = Form(...),
    time_initial: str = Form(...),
    time_final: str = Form(...),
    date_detection: str = Form(...),
):
    """
    ⚠️ **ENDPOINT DEPRECADO** - Use `/create` para nuevas implementaciones.
    
    Guarda una detección usando el formato legacy del sistema.
    
    - **image_id**: ID de la imagen relacionada (requerido)
    - **result**: Tipo de plaga detectada (requerido)
    - **prediction_value**: Valor de confianza de la predicción (requerido)
    - **time_initial**: Hora de inicio (formato HH:MM:SS) (requerido)
    - **time_final**: Hora de finalización (formato HH:MM:SS) (requerido)
    - **date_detection**: Fecha de detección (formato YYYY-MM-DD) (requerido)
    
    **Nota:** Este endpoint no incluye coordenadas GPS, porcentaje de plaga ni notas.
    Para funcionalidad completa, use el endpoint `/create`.
    """
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

@router.post("/create", response_model=DetectionResponse,
             summary="Crear nueva detección",
             description="Crea una nueva detección de plagas con coordenadas GPS y porcentaje de campo afectado.",
             responses={
                 201: {"description": "Detección creada exitosamente"},
                 401: {"description": "Token JWT inválido o expirado"},
                 404: {"description": "Campo o imagen no encontrados"},
                 422: {"description": "Datos de entrada inválidos"}
             })
async def create_detection(
    detection_data: DetectionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea una nueva detección de plagas con información completa.
    
    - **image_id**: ID de la imagen relacionada (requerido)
    - **field_id**: ID del campo donde se realizó la detección (requerido)
    - **result**: Tipo de plaga detectada (requerido)
    - **prediction_value**: Valor de confianza de la predicción (requerido)
    - **time_initial**: Hora de inicio de la detección (requerido)
    - **time_final**: Hora de finalización de la detección (requerido)
    - **date_detection**: Fecha de la detección (requerido)
    - **plague_percentage**: Porcentaje del campo afectado por la plaga (requerido)
    """
    print(f"DETECTION DATA: {detection_data}")
    detection = await DetectionService.create_detection(current_user.id, detection_data)
    return DetectionResponse.from_orm(detection)

@router.get("/", response_model=List[DetectionHistoryResponse],
            summary="Listar detecciones del usuario",
            description="Obtiene todas las detecciones del usuario autenticado.",
            responses={
                200: {"description": "Lista de detecciones obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"}
            })
async def get_detections(current_user: User = Depends(get_current_active_user)):
    """
    Obtiene todas las detecciones del usuario autenticado.
    
    Retorna una lista con todas las detecciones realizadas por el usuario,
    incluyendo información del campo, coordenadas y porcentaje de plaga.
    """
    detections = await DetectionService.get_detections_by_user(current_user.id)
    return [DetectionHistoryResponse.from_orm(d) for d in detections]

@router.get("/{detection_id}", response_model=DetectionHistoryResponse,
            summary="Obtener detección específica",
            description="Obtiene la información de una detección específica del usuario autenticado.",
            responses={
                200: {"description": "Detección obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Detección no encontrada"}
            })
async def get_detection(
    detection_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la información de una detección específica.
    
    - **detection_id**: ID de la detección a obtener
    """
    detection = await DetectionService.get_detection_by_id(detection_id, current_user.id)
    if not detection:
        raise HTTPException(
            status_code=404,
            detail="Detección no encontrada"
        )
    return DetectionHistoryResponse.from_orm(detection)

@router.put("/{detection_id}", response_model=DetectionHistoryResponse,
            summary="Actualizar detección",
            description="Actualiza la información de una detección existente.",
            responses={
                200: {"description": "Detección actualizada exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                404: {"description": "Detección no encontrada"},
                422: {"description": "Datos de entrada inválidos"}
            })
async def update_detection(
    detection_id: int,
    detection_data: DetectionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza la información de una detección existente.
    
    - **detection_id**: ID de la detección a actualizar
    - Todos los campos son opcionales en la actualización
    """
    detection = await DetectionService.update_detection(detection_id, current_user.id, detection_data)
    return DetectionHistoryResponse.from_orm(detection)

@router.delete("/{detection_id}",
               summary="Eliminar detección",
               description="Elimina una detección del usuario autenticado.",
               responses={
                   200: {"description": "Detección eliminada exitosamente"},
                   401: {"description": "Token JWT inválido o expirado"},
                   404: {"description": "Detección no encontrada"}
               })
async def delete_detection(
    detection_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina una detección del usuario autenticado.
    
    - **detection_id**: ID de la detección a eliminar
    
    ⚠️ **Advertencia**: Esta acción no se puede deshacer.
    """
    success = await DetectionService.delete_detection(detection_id, current_user.id)
    return {"message": "Detección eliminada exitosamente"}

@router.get("/boss/employees", response_model=List[DetectionHistoryResponse],
            summary="Listar detecciones de empleados",
            description="Obtiene todas las detecciones de los empleados vinculados al jefe autenticado.",
            responses={
                200: {"description": "Lista de detecciones de empleados obtenida exitosamente"},
                401: {"description": "Token JWT inválido o expirado"},
                403: {"description": "Solo jefes pueden usar este endpoint"}
            })
async def get_employee_detections(current_user: User = Depends(get_boss_user)):
    """
    Obtiene todas las detecciones de los empleados vinculados al jefe autenticado.
    
    Solo los jefes pueden usar este endpoint.
    Los jefes pueden ver las detecciones de sus empleados pero no modificarlas.
    """
    detections = await DetectionService.get_detections_by_boss(current_user.id)
    return [DetectionHistoryResponse.from_orm(detection) for detection in detections]
    

@router.post("/detect-pests", response_model=DetectionResponseBoxes,
             summary="Detectar plagas en imagen",
             description="Detecta plagas en una imagen de hoja usando Roboflow AI y devuelve bounding boxes.",
             responses={
                 200: {"description": "Detección completada exitosamente"},
                 400: {"description": "Archivo no es una imagen válida"},
                 422: {"description": "Datos de entrada inválidos"},
                 500: {"description": "Error procesando imagen"}
             })
async def detect_pests(
    file: UploadFile = File(...),
    return_image: bool = True
):
    """
    Detecta plagas en una imagen de hoja usando Roboflow AI.
    
    Este endpoint procesa una imagen y utiliza un modelo de IA entrenado para detectar
    y clasificar plagas en hojas de plantas. Devuelve información detallada sobre
    las detecciones encontradas.
    
    - **file**: Imagen de la hoja (JPG, PNG) - Requerido
    - **return_image**: Si devolver la imagen con bounding boxes dibujados (opcional, default: True)
    
    **Respuesta incluye:**
    - Lista de detecciones con coordenadas
    - Nivel de confianza de cada detección
    - Imagen procesada con bounding boxes (si se solicita)
    - Dimensiones de la imagen original
    
    **Tipos de archivo soportados:** JPG, JPEG, PNG
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
