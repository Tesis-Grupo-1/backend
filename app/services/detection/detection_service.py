from app.repositories import DetectionRepository
import cv2, base64
from app.schemas import BoundingBox

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
    
    