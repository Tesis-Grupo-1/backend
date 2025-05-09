# Usa la imagen base de Python
FROM python:3.12-slim

# Setea el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . /app

# Instala las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto en el que la app correrá (suponiendo que es un servidor)
EXPOSE 8000

# Define el comando para correr la aplicación
CMD ["python", "main.py"]
