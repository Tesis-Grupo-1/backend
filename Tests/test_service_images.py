import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from app.services.images.image_service import ImageService
from app.repositories import ImageRepository
from app.schemas import ImageUploadResponse
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError


@pytest.mark.asyncio
async def test_upload_image_success():
    """Test de subida exitosa de imagen"""

    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"dummy_image_data")

    mock_db_image = MagicMock()
    mock_db_image.id = 1
    mock_db_image.url_image = "https://test-bucket.s3.amazonaws.com/test_image.jpg"
    mock_db_image.name = "test_image.jpg"

    # Mock de settings
    with patch('app.services.images.image_service.settings') as mock_settings:
        mock_settings.AWS_ACCESS_KEY_ID = "test_access_key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test_secret_key"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_BUCKET_NAME = "test-bucket"

        # Mock de boto3.client y ImageRepository
        with patch('app.services.images.image_service.boto3.client') as mock_boto3_client, \
             patch('app.services.images.image_service.ImageRepository.create_image') as mock_create_image:
            
            # Configurar mock de S3
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3
            mock_s3.put_object.return_value = None
            
            # Configurar mock del repositorio
            mock_create_image.return_value = mock_db_image

            # Llamada al método upload_image
            response = await ImageService.upload_image(mock_file)

            # Verificaciones
            # Verificar que boto3.client fue llamado con los parámetros correctos
            mock_boto3_client.assert_called_once_with(
                "s3",
                aws_access_key_id="test_access_key",
                aws_secret_access_key="test_secret_key",
                region_name="us-east-1"
            )

            # Verificar que file.read() fue llamado
            mock_file.read.assert_called_once()

            # Verificar que put_object fue llamado correctamente
            mock_s3.put_object.assert_called_once_with(
                Bucket="test-bucket",
                Key="test_image.jpg",
                Body=b"dummy_image_data",
                ContentType="image/jpeg"
            )

            # Verificar que el repositorio fue llamado correctamente
            mock_create_image.assert_called_once_with(
                url_image="https://test-bucket.s3.amazonaws.com/test_image.jpg",
                name="test_image.jpg"
            )

            # Verificar la respuesta
            assert isinstance(response, ImageUploadResponse)
            assert response.url_image == "https://test-bucket.s3.amazonaws.com/test_image.jpg"
            assert response.name == "test_image.jpg"


@pytest.mark.asyncio
async def test_upload_image_no_credentials():
    """Test cuando no hay credenciales de AWS"""
    # Datos de prueba para el archivo
    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"dummy_image_data")

    # Mock de settings
    with patch('app.services.images.image_service.settings') as mock_settings:
        mock_settings.AWS_ACCESS_KEY_ID = "test_access_key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test_secret_key"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_BUCKET_NAME = "test-bucket"

        # Mock de boto3.client para lanzar NoCredentialsError
        with patch('app.services.images.image_service.boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3
            # El error se lanza en put_object, no en client()
            mock_s3.put_object.side_effect = NoCredentialsError()

            # Verificar que se lanza la excepción correcta
            with pytest.raises(HTTPException) as exc_info:
                await ImageService.upload_image(mock_file)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Credenciales de AWS no encontradas o incorrectas."


@pytest.mark.asyncio
async def test_upload_image_partial_credentials():
    """Test cuando faltan credenciales parciales de AWS"""
    # Datos de prueba para el archivo
    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"dummy_image_data")

    # Mock de settings
    with patch('app.services.images.image_service.settings') as mock_settings:
        mock_settings.AWS_ACCESS_KEY_ID = "test_access_key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test_secret_key"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_BUCKET_NAME = "test-bucket"

        # Mock de boto3.client
        with patch('app.services.images.image_service.boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3
            # El error se lanza en put_object
            mock_s3.put_object.side_effect = PartialCredentialsError(
                provider="aws", 
                cred_var="AWS_ACCESS_KEY_ID"
            )

            # Verificar que se lanza la excepción correcta
            with pytest.raises(HTTPException) as exc_info:
                await ImageService.upload_image(mock_file)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Faltan credenciales de AWS necesarias."


@pytest.mark.asyncio
async def test_upload_image_boto_core_error():
    """Test cuando ocurre un error de BotoCore"""
    # Datos de prueba para el archivo
    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"dummy_image_data")

    # Mock de settings
    with patch('app.services.images.image_service.settings') as mock_settings:
        mock_settings.AWS_ACCESS_KEY_ID = "test_access_key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test_secret_key"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_BUCKET_NAME = "test-bucket"

        # Mock de boto3.client
        with patch('app.services.images.image_service.boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3
            # El error se lanza en put_object
            mock_s3.put_object.side_effect = BotoCoreError()

            # Verificar que se lanza la excepción correcta
            with pytest.raises(HTTPException) as exc_info:
                await ImageService.upload_image(mock_file)
            
            assert exc_info.value.status_code == 500
            assert "Error al interactuar con AWS S3:" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_image_repository_error():
    """Test cuando el repositorio falla"""
    # Datos de prueba para el archivo
    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"dummy_image_data")

    # Mock de settings
    with patch('app.services.images.image_service.settings') as mock_settings:
        mock_settings.AWS_ACCESS_KEY_ID = "test_access_key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test_secret_key"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_BUCKET_NAME = "test-bucket"

        # Mock de boto3.client y ImageRepository
        with patch('app.services.images.image_service.boto3.client') as mock_boto3_client, \
             patch('app.services.images.image_service.ImageRepository.create_image') as mock_create_image:
            
            # Configurar mock de S3 (exitoso)
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3
            mock_s3.put_object.return_value = None
            
            # Configurar mock del repositorio para que falle
            mock_create_image.side_effect = Exception("Database error")

            # Verificar que la excepción se propaga
            with pytest.raises(Exception, match="Database error"):
                await ImageService.upload_image(mock_file)


@pytest.mark.asyncio
async def test_upload_image_invalid_file():
    """Test con archivo None"""
    with pytest.raises(AttributeError):
        await ImageService.upload_image(None)


# Fixture para configurar mocks comunes si es necesario
@pytest.fixture
def mock_settings():
    """Fixture para configurar settings de prueba"""
    with patch('app.services.images.image_service.settings') as mock_settings:
        mock_settings.AWS_ACCESS_KEY_ID = "test_access_key"
        mock_settings.AWS_SECRET_ACCESS_KEY = "test_secret_key"
        mock_settings.AWS_REGION = "us-east-1"
        mock_settings.AWS_BUCKET_NAME = "test-bucket"
        yield mock_settings