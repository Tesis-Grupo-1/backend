from app.models import Detection

class DetectionRepository:
    """
    Repositorio para la gestión de detecciones en la base de datos.
    """
    
    @staticmethod
    async def create_detection(image_id: int, result: str, prediction_value: str) -> Detection:
        """
        Crea una nueva detección en la base de datos.
        """
        detection = await Detection.create(
            image_id=image_id,
            prediction_value=prediction_value,
            result=result
        )
        return detection