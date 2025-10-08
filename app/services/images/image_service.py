import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from fastapi import UploadFile, HTTPException, status
from app.core import settings
from app.repositories import ImageRepository
from app.schemas import ImageUploadResponse, ImageValidation, DetectionImagesResponse, ImageResponse
from botocore.exceptions import BotoCoreError, NoCredentialsError, PartialCredentialsError
from app.models import Images, Detection
from datetime import datetime

class ImageService:

    @staticmethod
    async def upload_image(file: UploadFile, porcentaje_plaga: float) -> ImageUploadResponse:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        file_content = await file.read()
        
        try:
            s3.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=file.filename,
                Body=file_content,
                ContentType=file.content_type
            )

            url = f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{file.filename}"

            resp = await ImageRepository.create_image(
                url_image=url,
                name=file.filename,
                porcentaje_plaga=porcentaje_plaga
            )
            return ImageUploadResponse.from_orm(resp)

        except NoCredentialsError:
            raise HTTPException(status_code=400, detail="Credenciales de AWS no encontradas o incorrectas.")
        except PartialCredentialsError:
            raise HTTPException(status_code=400, detail="Faltan credenciales de AWS necesarias.")
        except BotoCoreError as e:
            raise HTTPException(status_code=500, detail=f"Error al interactuar con AWS S3: {e}")


    @staticmethod
    async def get_images_by_detection(detection_id: int, user_id: int):
        """Obtiene todas las imágenes de una detección específica"""
        
        # Verificar que la detección pertenece al usuario
        detection = await Detection.filter(
            id_detection=detection_id,
            user_id=user_id
        ).prefetch_related('field').first()
        
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detección no encontrada"
            )
        
        # Obtener todas las imágenes de la detección
        images = await Images.filter(detection_id=detection_id).all()
        
        # Calcular estadísticas
        total_images = len(images)
        validated_images = sum(1 for img in images if img.is_validated)
        false_positives = sum(1 for img in images if img.is_false_positive)
        
        # Convertir las imágenes a diccionarios
        images_data = [
            {
                "id_image": img.id_image,
                "image_path": img.image_path,
                "porcentaje_plaga": img.porcentaje_plaga,
                "created_at": img.created_at.isoformat() if img.created_at else None,
                "is_validated": img.is_validated,
                "is_false_positive": img.is_false_positive,
                "validated_at": img.validated_at.isoformat() if img.validated_at else None,
                "detection_id": detection_id
            }
            for img in images
        ]
        
        return {
            "detection_id": detection_id,
            "field_name": detection.field.name if detection.field else "Campo desconocido",
            "detection_date": str(detection.date_detection),
            "total_images": total_images,
            "validated_images": validated_images,
            "false_positives": false_positives,
            "images": images_data  
        }
    
    @staticmethod
    async def validate_image(image_id: int, user_id: int, validation: ImageValidation):
        """Valida una imagen marcándola como falso positivo o correcta"""
        
        # Verificar que la imagen pertenece al usuario
        image = await Images.filter(id_image=image_id).prefetch_related('detection').first()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imagen no encontrada"
            )
        
        # Verificar que el usuario es dueño de la detección
        detection = await Detection.filter(
            id_detection=image.detection_id,
            user_id=user_id
        ).first()
        
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para validar esta imagen"
            )
        
        # Actualizar la validación
        image.is_validated = True
        image.is_false_positive = validation.is_false_positive
        image.validated_at = datetime.now()
        await image.save()
        
        return image
    
    @staticmethod
    async def get_false_positive_stats(user_id: int):
        """Obtiene estadísticas de falsos positivos del usuario"""
        
        # Obtener todas las imágenes validadas del usuario
        detections = await Detection.filter(user_id=user_id).values_list('id_detection', flat=True)
        
        total_validated = await Images.filter(
            detection_id__in=detections,
            is_validated=True
        ).count()
        
        total_false_positives = await Images.filter(
            detection_id__in=detections,
            is_false_positive=True
        ).count()
        
        false_positive_rate = (total_false_positives / total_validated * 100) if total_validated > 0 else 0
        
        return {
            "total_validated_images": total_validated,
            "total_false_positives": total_false_positives,
            "false_positive_rate": round(false_positive_rate, 2),
            "accuracy_rate": round(100 - false_positive_rate, 2)
        }