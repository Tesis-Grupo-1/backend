# Usa la imagen base de Python 3.12
FROM python:3.12-slim

# Setea el directorio de trabajo en el contenedor
WORKDIR /app

# Copia todos los archivos del proyecto en el contenedor
COPY . /app

# Instala las dependencias de la aplicación desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto en el que la app correrá (suponiendo que es un servidor)
EXPOSE 8000

# Define el comando para correr la aplicación
CMD ["uvicorn", "main:app", "--reload"]
