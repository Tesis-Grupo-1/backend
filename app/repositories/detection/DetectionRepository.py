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
    
    @staticmethod
    async def save_detection_time(
        detection_id: int, 
        time_initial: float, 
        time_final: float, 
        time_detection: float
    ) -> Detection:
        """
        Guarda el tiempo de detección en la base de datos.
        """
        detection = await Detection.get(id_detection=detection_id)
        print(f"Guardando tiempos para la detección {detection_id}: "
              f"Inicial={time_initial}, Final={time_final}, Detección={time_detection}")
        if not detection:
            raise ValueError(f"Detection with id {detection_id} not found.")
        detection.time_initial = time_initial
        detection.time_final = time_final
        detection.time_detection = time_detection
        await detection.save()
        return detection