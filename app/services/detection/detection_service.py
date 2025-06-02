from app.repositories import DetectionRepository


class DetectionService:


    @staticmethod
    async def save_time(image_id: int, result: str, prediction_value: str, time_initial: str, time_final: str, date_detection: str) -> DetectionRepository:
        """
        Guarda el tiempo de detección en la base de datos.
        """
        print("="*10)
        print("service")
        print(f"Image_id: {image_id}, result: {result}, prediction_value: {prediction_value}, time_initial: {time_initial}, time_final: {time_final}, date_detection: {date_detection}")
        
        detection_new = await DetectionRepository.save_detection(
            image_id=image_id,
            result=result,
            prediction_value=prediction_value,
            time_initial=time_initial,
            time_final=time_final,
            date_detection=date_detection
        )
        return detection_new