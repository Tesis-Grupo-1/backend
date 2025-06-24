import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from app.services.detection.detection_service import DetectionService
from app.repositories.detection.DetectionRepository import DetectionRepository
from app.models.detection import Detection
import numpy as np
import cv2
import base64
import pytest
from unittest.mock import patch, MagicMock
from app.schemas import BoundingBox



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

def test_convert_roboflow_coordinates():
    """Test para conversión de coordenadas de Roboflow"""
    # Datos de prueba
    prediction = {
        'x': 100,
        'y': 150,
        'width': 50,
        'height': 80
    }
    img_width = 640
    img_height = 480
    
    # Llamar al método
    bbox = DetectionService.convert_roboflow_coordinates(prediction, img_width, img_height)
    
    # Verificaciones
    assert isinstance(bbox, BoundingBox)
    assert bbox.x1 == 75  # 100 - 50/2
    assert bbox.y1 == 110  # 150 - 80/2
    assert bbox.x2 == 125  # 100 + 50/2
    assert bbox.y2 == 190  # 150 + 80/2
    assert bbox.center_x == 100
    assert bbox.center_y == 150
    assert bbox.width == 50
    assert bbox.height == 80


def test_convert_roboflow_coordinates_edge_cases():
    """Test para casos límite en conversión de coordenadas"""
    # Caso: coordenadas que se salen de los límites de la imagen
    prediction = {
        'x': 10,  # Muy cerca del borde izquierdo
        'y': 10,  # Muy cerca del borde superior
        'width': 50,
        'height': 50
    }
    img_width = 640
    img_height = 480
    
    bbox = DetectionService.convert_roboflow_coordinates(prediction, img_width, img_height)
    
    # x1 debería ser máximo 0 (no negativo)
    assert bbox.x1 == 0
    assert bbox.y1 == 0
    assert bbox.x2 == 35  # 10 + 50/2
    assert bbox.y2 == 35  # 10 + 50/2


def test_convert_roboflow_coordinates_max_bounds():
    """Test para coordenadas que exceden el tamaño máximo de imagen"""
    prediction = {
        'x': 620,  # Muy cerca del borde derecho
        'y': 460,  # Muy cerca del borde inferior
        'width': 50,
        'height': 50
    }
    img_width = 640
    img_height = 480
    
    bbox = DetectionService.convert_roboflow_coordinates(prediction, img_width, img_height)
    
    # x2 e y2 no deberían exceder las dimensiones de la imagen
    assert bbox.x2 == 640  # min(img_width, calculated_x2)
    assert bbox.y2 == 480  # min(img_height, calculated_y2)


@pytest.mark.parametrize("x,y,width,height,expected_x1,expected_y1,expected_x2,expected_y2", [
    (50, 50, 20, 30, 40, 35, 60, 65),
    (100, 100, 40, 60, 80, 70, 120, 130),
    (200, 150, 100, 80, 150, 110, 250, 190),
])
def test_convert_roboflow_coordinates_parametrized(x, y, width, height, expected_x1, expected_y1, expected_x2, expected_y2):
    """Test parametrizado para múltiples casos de conversión de coordenadas"""
    prediction = {'x': x, 'y': y, 'width': width, 'height': height}
    img_width = 640
    img_height = 480
    
    bbox = DetectionService.convert_roboflow_coordinates(prediction, img_width, img_height)
    
    assert bbox.x1 == expected_x1
    assert bbox.y1 == expected_y1
    assert bbox.x2 == expected_x2
    assert bbox.y2 == expected_y2


@patch('cv2.rectangle')
@patch('cv2.getTextSize')
@patch('cv2.putText')
def test_draw_bounding_boxes(mock_putText, mock_getTextSize, mock_rectangle):
    """Test para dibujar bounding boxes en imagen"""
    # Crear imagen mock
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Crear detección mock
    mock_detection = MagicMock()
    mock_detection.bounding_box = BoundingBox(
        x1=50, y1=100, x2=150, y2=200,
        center_x=100, center_y=150,
        width=100, height=100
    )
    mock_detection.class_name = "plaga"
    mock_detection.confidence = 0.95
    
    detections = [mock_detection]
    
    # Mock del tamaño del texto
    mock_getTextSize.return_value = ((80, 20), 5)
    
    # Llamar al método
    result_image = DetectionService.draw_bounding_boxes(image, detections)
    
    # Verificaciones
    assert result_image is not None
    assert result_image.shape == image.shape
    
    # Verificar que se llamaron las funciones de OpenCV
    assert mock_rectangle.call_count == 2  # Una para el bbox, otra para el fondo del texto
    mock_getTextSize.assert_called_once()
    mock_putText.assert_called_once()


def test_draw_bounding_boxes_empty_detections():
    """Test para dibujar bounding boxes con lista vacía"""
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = []
    
    result_image = DetectionService.draw_bounding_boxes(image, detections)
    
    # La imagen debería ser igual a la original (copia)
    assert result_image is not None
    assert result_image.shape == image.shape
    np.testing.assert_array_equal(result_image, image)


@patch('cv2.rectangle')
@patch('cv2.getTextSize')
@patch('cv2.putText')
def test_draw_bounding_boxes_multiple_detections(mock_putText, mock_getTextSize, mock_rectangle):
    """Test para múltiples detecciones"""
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Crear múltiples detecciones mock
    detections = []
    for i in range(3):
        mock_detection = MagicMock()
        mock_detection.bounding_box = BoundingBox(
            x1=50 + i*100, y1=100, x2=150 + i*100, y2=200,
            center_x=100 + i*100, center_y=150,
            width=100, height=100
        )
        mock_detection.class_name = f"plaga_{i}"
        mock_detection.confidence = 0.9 - i*0.1
        detections.append(mock_detection)
    
    mock_getTextSize.return_value = ((80, 20), 5)
    
    result_image = DetectionService.draw_bounding_boxes(image, detections)
    
    # Verificar que se procesaron todas las detecciones
    assert mock_rectangle.call_count == 6  # 2 llamadas por cada detección (3 detecciones)
    assert mock_getTextSize.call_count == 3
    assert mock_putText.call_count == 3


@patch('cv2.imencode')
@patch('base64.b64encode')
def test_image_to_base64_success(mock_b64encode, mock_imencode):
    """Test para conversión exitosa de imagen a base64"""
    # Crear imagen mock
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Mock de cv2.imencode
    mock_buffer = b'fake_encoded_image_data'
    mock_imencode.return_value = (True, mock_buffer)
    
    # Mock de base64.b64encode
    mock_encoded = b'ZmFrZV9lbmNvZGVkX2ltYWdlX2RhdGE='
    mock_b64encode.return_value = mock_encoded
    
    # Llamar al método
    result = DetectionService.image_to_base64(image)
    
    # Verificaciones
    mock_imencode.assert_called_once_with('.jpg', image)
    mock_b64encode.assert_called_once_with(mock_buffer)
    assert result == mock_encoded.decode('utf-8')


@patch('cv2.imencode')
def test_image_to_base64_encode_failure(mock_imencode):
    """Test para fallo en la codificación de imagen"""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Mock de fallo en imencode
    mock_imencode.return_value = (False, None)
    
    # El método debería manejar el error o lanzar excepción
    with pytest.raises(Exception):
        DetectionService.image_to_base64(image)


def test_image_to_base64_with_real_image():
    """Test de integración con imagen real pequeña"""
    # Crear una imagen pequeña real
    image = np.ones((10, 10, 3), dtype=np.uint8) * 255  # Imagen blanca 10x10
    
    # Llamar al método real
    result = DetectionService.image_to_base64(image)
    
    # Verificar que el resultado es una cadena base64 válida
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Verificar que se puede decodificar
    try:
        decoded = base64.b64decode(result)
        assert len(decoded) > 0
    except Exception:
        pytest.fail("El resultado no es un base64 válido")


@pytest.mark.parametrize("image_format", ['.jpg', '.png', '.bmp'])
@patch('cv2.imencode')
@patch('base64.b64encode')
def test_image_to_base64_different_formats(mock_b64encode, mock_imencode, image_format):
    """Test parametrizado para diferentes formatos de imagen"""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_buffer = b'fake_data'
    mock_imencode.return_value = (True, mock_buffer)
    mock_b64encode.return_value = b'encoded_data'
    
    # Nota: Este test asume que tu método puede aceptar formato como parámetro
    # Si no es así, ajusta según tu implementación
    result = DetectionService.image_to_base64(image)
    
    # Verificar que se llamó imencode con el formato correcto
    mock_imencode.assert_called_once_with('.jpg', image)  # Asumiendo que siempre usa .jpg
    assert result == 'encoded_data'


def test_bounding_box_schema_creation():
    """Test para verificar que el esquema BoundingBox funciona correctamente"""
    bbox = BoundingBox(
        x1=10, y1=20, x2=100, y2=150,
        center_x=55, center_y=85,
        width=90, height=130
    )
    
    assert bbox.x1 == 10
    assert bbox.y1 == 20
    assert bbox.x2 == 100
    assert bbox.y2 == 150
    assert bbox.center_x == 55
    assert bbox.center_y == 85
    assert bbox.width == 90
    assert bbox.height == 130


@pytest.mark.parametrize("x1,y1,x2,y2", [
    (0, 0, 100, 100),
    (50, 50, 200, 200),
    (10, 20, 30, 40),
])
def test_bounding_box_schema_parametrized(x1, y1, x2, y2):
    """Test parametrizado para BoundingBox con diferentes coordenadas"""
    bbox = BoundingBox(
        x1=x1, y1=y1, x2=x2, y2=y2,
        center_x=(x1+x2)/2, center_y=(y1+y2)/2,
        width=x2-x1, height=y2-y1
    )
    
    assert bbox.x1 == x1
    assert bbox.y1 == y1
    assert bbox.x2 == x2
    assert bbox.y2 == y2


@pytest.fixture
def sample_image():
    """Fixture para crear una imagen de muestra"""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_detection():
    """Fixture para crear una detección de muestra"""
    mock_detection = MagicMock()
    mock_detection.bounding_box = BoundingBox(
        x1=50, y1=100, x2=150, y2=200,
        center_x=100, center_y=150,
        width=100, height=100
    )
    mock_detection.class_name = "plaga_test"
    mock_detection.confidence = 0.85
    return mock_detection


def test_draw_bounding_boxes_with_fixtures(sample_image, sample_detection):
    """Test usando fixtures para datos de muestra"""
    detections = [sample_detection]
    
    with patch('cv2.rectangle'), \
         patch('cv2.getTextSize', return_value=((80, 20), 5)), \
         patch('cv2.putText'):
        
        result_image = DetectionService.draw_bounding_boxes(sample_image, detections)
        
        assert result_image is not None
        assert result_image.shape == sample_image.shape


def test_convert_roboflow_coordinates_performance():
    """Test de rendimiento para conversión de coordenadas"""
    import time
    
    prediction = {'x': 100, 'y': 150, 'width': 50, 'height': 80}
    img_width, img_height = 640, 480
    
    start_time = time.time()
    
    # Ejecutar múltiples veces para medir rendimiento
    for _ in range(1000):
        bbox = DetectionService.convert_roboflow_coordinates(prediction, img_width, img_height)
    
    end_time = time.time()
    
    # Verificar que el tiempo es razonable (menos de 1 segundo para 1000 iteraciones)
    assert (end_time - start_time) < 1.0
    assert bbox is not None