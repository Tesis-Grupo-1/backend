import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from app.repositories import DetectionRepository


class DetectionService:
    model = None  # Variable de clase para almacenar el modelo cargado

    @staticmethod
    async def load_model():
        if DetectionService.model is None:
            DetectionService.model = tf.keras.models.load_model('modelo\\modelo_entrenado.h5')
            print("Modelo cargado exitosamente.")
        return DetectionService.model

    @staticmethod
    async def preprocess_image(image: Image):
        # Verificar que el objeto `image` es realmente una instancia de PIL.Image
        if not isinstance(image, Image.Image):
            raise ValueError("El objeto no es una imagen válida de PIL")

        # Hacer una copia de la imagen para evitar problemas de referencias de memoria
        image = image.copy()

        # Redimensionar la imagen a 224x224
        image = image.resize((224, 224))

        # Intentar convertir la imagen a formato RGB (si es necesario)
        try:
            image = image.convert('RGB')
        except Exception as e:
            raise ValueError(f"Error al convertir la imagen a RGB: {e}")

        # Convertir la imagen en un array de NumPy
        image_array = img_to_array(image)

        # Normalizar la imagen a un rango de 0 a 1
        image_array = image_array / 255.0

        # Añadir una dimensión extra para que el modelo lo reciba en el formato adecuado (batch_size, height, width, channels)
        image_array = np.expand_dims(image_array, axis=0)

        return image_array

    @staticmethod 
    async def detect_plaga(img_array, id_image) -> dict:
        # Cargar el modelo una sola vez
        model = await  DetectionService.load_model()
        
        # Realizar la predicción
        prediction = model.predict(img_array)
        prediction_value = round(float(prediction[0][0]), 2)
        
        # Si la salida del modelo es 0 o 1, puedes hacer una comparación
        if prediction[0] > 0.5:
            plaga = True
        else:
            plaga = False

        # Imprimir el resultado de la predicción (probabilidad de la plaga)
        print(f"Predicción (Probabilidad de Plaga): {prediction_value}")
        
        await DetectionRepository.create_detection(image_id=id_image, result=plaga, prediction_value=prediction_value)
        
        return {"plaga": plaga, "prediction_value": prediction_value}
