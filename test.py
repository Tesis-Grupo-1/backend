import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array  # type: ignore
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input  # type: ignore
from tensorflow.keras.models import load_model  # type: ignore

# Ruta de la imagen a probar
img_path = 'modelo\Pupa\image_75.jpeg'  # Cambia la ruta a tu imagen

# Cargar la imagen y preprocesarla
img = load_img(img_path, target_size=(224, 224))  # Redimensionar la imagen
img_array = img_to_array(img) / 255.0  # Normalizar la imagen
img_array = np.expand_dims(img_array, axis=0)  # Añadir una dimensión para el batch
img_array = preprocess_input(img_array)  # Preprocesamiento para ResNet50

print(img_array.shape)


# Cargar el modelo entrenado
model = load_model('modelo/modelo_entrenado_resnet.h5')  # Cargar el modelo desde el archivo .h5

# Obtener la predicción
prediction = model.predict(img_array)

print(f"Predicción: {prediction[0][0]}")  # Imprimir la predicción

# Mostrar la imagen y la predicción
plt.imshow(img)
plt.axis('off')
plt.title(f"Predicción: {'Plaga' if prediction > 0.5 else 'Sana'}")  # Ajusta según tu umbral
plt.show()
