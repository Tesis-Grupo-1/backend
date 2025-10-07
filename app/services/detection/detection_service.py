from app.repositories import DetectionRepository
from app.models.detection import Detection
from app.models.images import Images
from app.models.field import Field
from app.models.user import User
from app.schemas import DetectionCreate, DetectionUpdate
from fastapi import HTTPException, status
import cv2, base64
from app.schemas import BoundingBox
from typing import List, Optional

class DetectionService:

    @staticmethod
    async def save_time(image_id: int, result: str, prediction_value: str, time_initial: str, time_final: str, date_detection: str) -> DetectionRepository:
        """
        Guarda el tiempo de detección en la base de datos.
        """
        
        detection_new = await DetectionRepository.save_detection(
            image_id=image_id,
            result=result,
            prediction_value=prediction_value,
            time_initial=time_initial,
            time_final=time_final,
            date_detection=date_detection
        )
        return detection_new
    
    @staticmethod
    async def create_detection(user_id: int, detection_data: DetectionCreate) -> Detection:
        """Crea una nueva detección con múltiples imágenes"""

        # Verificar usuario
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar campo
        field = await Field.get_or_none(id=detection_data.field_id, user_id=user_id)
        if not field:
            raise HTTPException(status_code=404, detail="Campo no encontrado")

        # Crear la detección base
        detection = await Detection.create(
            user_id=user_id,
            field_id=detection_data.field_id,
            result=detection_data.result,
            prediction_value=detection_data.prediction_value,
            time_initial=detection_data.time_initial,
            time_final=detection_data.time_final,
            date_detection=detection_data.date_detection,
            plague_percentage=detection_data.plague_percentage,
        )

        # Asociar imágenes si existen
        if detection_data.image_ids:
            for img_id in detection_data.image_ids:
                image = await Images.get_or_none(id_image=img_id)
                if image:
                    image.detection = detection
                    await image.save()

        return detection
    
    @staticmethod
    async def get_detections_by_user(user_id: int) -> List[Detection]:
        """Obtiene todas las detecciones de un usuario"""
        return await Detection.filter(user_id=user_id).prefetch_related('field', 'images')

    
    @staticmethod
    async def get_detection_by_id(detection_id: int, user_id: int) -> Optional[Detection]:
        """Obtiene una detección específica de un usuario"""
        return await Detection.get_or_none(id_detection=detection_id, user_id=user_id).prefetch_related('field', 'images')

    
    @staticmethod
    async def update_detection(detection_id: int, user_id: int, detection_data: DetectionUpdate) -> Detection:
        """Actualiza una detección"""
        detection = await Detection.get_or_none(id_detection=detection_id, user_id=user_id)
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detección no encontrada"
            )
        
        # Actualizar campos
        for field_name, value in detection_data.dict(exclude_unset=True).items():
            if hasattr(detection, field_name):
                setattr(detection, field_name, value)
        
        await detection.save()
        return detection
    
    @staticmethod
    async def delete_detection(detection_id: int, user_id: int) -> bool:
        """Elimina una detección"""
        detection = await Detection.get_or_none(id_detection=detection_id, user_id=user_id)
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detección no encontrada"
            )
        
        await detection.delete()
        return True
    
    @staticmethod
    async def get_detections_by_boss(boss_id: int) -> List[Detection]:
        """Obtiene todas las detecciones de los empleados de un jefe"""
        # Obtener empleados del jefe
        employees = await User.filter(boss_id=boss_id, role="employee")
        employee_ids = [emp.id for emp in employees]
        
        # Obtener detecciones de los empleados
        return await Detection.filter(user_id__in=employee_ids).prefetch_related('field', 'images', 'user')
    
    @staticmethod
    def convert_roboflow_coordinates(prediction, img_width, img_height):
        """Convierte coordenadas de Roboflow (centro + dimensiones) a formato estándar"""
        center_x = prediction['x']
        center_y = prediction['y']
        width = prediction['width']
        height = prediction['height']
        
        # Convertir a coordenadas de esquina
        x1 = max(0, int(center_x - width / 2))
        y1 = max(0, int(center_y - height / 2))
        x2 = min(img_width, int(center_x + width / 2))
        y2 = min(img_height, int(center_y + height / 2))
        
        return BoundingBox(
            x1=x1, y1=y1, x2=x2, y2=y2,
            center_x=center_x, center_y=center_y,
            width=width, height=height
        )

    @staticmethod
    def draw_bounding_boxes(image, detections):
        """Dibuja bounding boxes en la imagen"""
        img_copy = image.copy()
        
        for detection in detections:
            bbox = detection.bounding_box
            
            # Dibujar rectángulo
            cv2.rectangle(img_copy, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 2)
            
            # Preparar texto
            label = f"{detection.class_name} ({detection.confidence*100:.1f}%)"
            
            # Obtener tamaño del texto
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Dibujar fondo del texto
            cv2.rectangle(img_copy, 
                        (bbox.x1, bbox.y1 - text_height - 10), 
                        (bbox.x1 + text_width, bbox.y1), 
                        (0, 255, 0), -1)
            
            # Dibujar texto
            cv2.putText(img_copy, label, (bbox.x1, bbox.y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return img_copy

    def image_to_base64(image):
        """Convierte imagen OpenCV a base64"""
        _, buffer = cv2.imencode('.jpg', image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return img_base64
    
    