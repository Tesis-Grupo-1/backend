import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from fastapi import UploadFile, HTTPException
from app.core import settings
from app.repositories import ImageRepository
from app.schemas import ImageUploadResponse
from botocore.exceptions import BotoCoreError, NoCredentialsError, PartialCredentialsError

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
