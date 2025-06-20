import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from app.services.detection.detection_service import DetectionService
from app.repositories.detection.DetectionRepository import DetectionRepository
from app.models.detection import Detection


@pytest.mark.asyncio
async def test_save_time_success():
    # Datos válidos para la prueba
    image_id = 1
    result = "plaga_detectada"
    prediction_value = "0.98"
    time_initial = "10:00:00"
    time_final = "10:10:00"
    date_detection = "2025-06-19"

    # Simulamos el retorno del repositorio
    mock_detection = MagicMock(spec=Detection)
    mock_detection.id_detection = 1
    mock_detection.result = result
    mock_detection.prediction_value = prediction_value

    # Usamos patch para simular la función de `save_detection` del repositorio
    with patch.object(DetectionRepository, 'save_detection', return_value=mock_detection):
        # Llamamos al método del servicio
        detection = await DetectionService.save_time(
            image_id=image_id,
            result=result,
            prediction_value=prediction_value,
            time_initial=time_initial,
            time_final=time_final,
            date_detection=date_detection
        )

        # Verifica que la función save_detection haya sido llamada con los parámetros correctos
        DetectionRepository.save_detection.assert_called_once_with(
            image_id=image_id,
            result=result,
            prediction_value=prediction_value,
            time_initial=time_initial,
            time_final=time_final,
            date_detection=date_detection
        )

        # Verifica que el objeto retornado sea el mock
        assert detection == mock_detection
        assert detection.id_detection == 1
        assert detection.result == result
        assert detection.prediction_value == prediction_value


@pytest.mark.asyncio
async def test_save_time_failure():
    # Datos de prueba
    image_id = 1
    result = "plaga_detectada"
    prediction_value = "0.98"
    time_initial = "10:00:00"
    time_final = "10:10:00"
    date_detection = "2025-06-19"

    # Simulamos que `save_detection` lanza una excepción
    with patch.object(DetectionRepository, 'save_detection', side_effect=Exception("Error al guardar")):
        with pytest.raises(Exception, match="Error al guardar"):
            await DetectionService.save_time(
                image_id=image_id,
                result=result,
                prediction_value=prediction_value,
                time_initial=time_initial,
                time_final=time_final,
                date_detection=date_detection
            )


@pytest.mark.asyncio
async def test_save_time_invalid_format():
    # Datos con formato de hora inválido
    image_id = 1
    result = "plaga_detectada"
    prediction_value = "0.98"
    time_initial = "2025-06-19T10:00:00"  # Formato incorrecto (fecha + hora)
    time_final = "10:10:00"
    date_detection = "2025-06-19"

    # Simulamos que `DetectionRepository.save_detection` lance un ValueError
    with patch.object(DetectionRepository, 'save_detection', side_effect=ValueError("Invalid isoformat string")):
        # Llamada al método y verificación de la excepción
        with pytest.raises(ValueError):
            await DetectionService.save_time(
                image_id=image_id,
                result=result,
                prediction_value=prediction_value,
                time_initial=time_initial,
                time_final=time_final,
                date_detection=date_detection
            )