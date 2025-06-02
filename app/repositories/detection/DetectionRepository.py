from app.models import Detection
from datetime import time, date

class DetectionRepository:
    """
    Repositorio para la gestión de detecciones en la base de datos.
    """


    @staticmethod
    async def save_detection(
        image_id: int,
        result: str,
        prediction_value: str,
        time_initial: str, 
        time_final: str, 
        date_detection: str
    ) -> Detection:
        """
        Guarda los resultados de la deteccion
        """
        print("="*10)
        print("repository")
        print(f"Image_id: {image_id}, result: {result}, prediction_value: {prediction_value}, time_initial: {time_initial}, time_final: {time_final}, date_detection: {date_detection}")
        
        try:
            time_initial_obj = time.fromisoformat(time_initial)
            time_final_obj = time.fromisoformat(time_final)
            date_detection_obj = date.fromisoformat(date_detection)
        except ValueError as ve:
            print(f"Error al parsear campos de tiempo: {str(ve)}")
            raise ve


        detection_new = await Detection.create(
            image_id=image_id,
            result=result,
            prediction_value=prediction_value,
            time_initial=time_initial_obj,
            time_final=time_final_obj,
            date_detection=date_detection_obj
        )
        return detection_new