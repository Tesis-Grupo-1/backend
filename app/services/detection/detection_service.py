import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array #type: ignore
from PIL import Image
from app.repositories import DetectionRepository
import os

class DetectionService:
    model = None  # Variable de clase para almacenar el modelo cargado

    @staticmethod
    async def load_model():
        if DetectionService.model is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            model_path = os.path.join(base_dir, 'modelo', 'modelo_entrenado_resnet.h5')

            DetectionService.model = tf.keras.models.load_model(model_path)
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
        model = await DetectionService.load_model()

        # Realizar la predicción
        prediction = model.predict(img_array)  # shape (1, 3), ejemplo [[0.1, 0.7, 0.2]]

        # Obtener índice de la clase con mayor probabilidad
        predicted_class_index = np.argmax(prediction[0])
        predicted_class_prob = float(prediction[0][predicted_class_index])

        # Mapeo de índices a etiquetas
        class_labels = ['plaga', 'sana', 'otros']
        predicted_class_label = class_labels[predicted_class_index]

        print(f"Predicción: Clase={predicted_class_label}, Probabilidad={predicted_class_prob:.2f}")

        # Definir si es plaga o no según la etiqueta
        plaga = predicted_class_label == 'plaga'

        # Guardar en base de datos
        await DetectionRepository.create_detection(
            image_id=id_image, 
            result=plaga, 
            prediction_value=predicted_class_prob
        )

        return {"plaga": plaga, "prediction_value": predicted_class_prob, "class_label": predicted_class_label}
