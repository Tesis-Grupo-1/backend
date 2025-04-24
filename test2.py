import tensorflow as tf

# Cargar el modelo
model = tf.keras.models.load_model("modelo\\modelo_entrenado.h5")

# Inspeccionar la arquitectura del modelo
model.summary()

# O también puedes revisar la entrada
input_shape = model.input_shape
print(f"Input shape of the model: {input_shape}")
