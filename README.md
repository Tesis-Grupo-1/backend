# Backend MinaScan


## Descripción

Este proyecto es el backend de una aplicación móvil diseñada para detectar la plaga _Liriomyza huidobrensis_ (Mosca Minadora) a partir de imágenes. Utiliza técnicas de Deep Learning basadas en transfer learning con el modelo ResNet50 para realizar una clasificación multiclase que distingue entre plaga, hojas sanas y otras imágenes no relacionadas. Gracias a este enfoque, se mejora la precisión y robustez del sistema de detección, facilitando un diagnóstico rápido y efectivo para el control fitosanitario.

## Tabla de Contenidos

- [Instalación](#instalación)
- [Uso](#uso)
- [Configuración](#configuración)
- [Tecnologías](#tecnologías)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Instalación

Pasos para instalar y configurar el proyecto localmente.

Ejemplo:

```bash
git clone https://github.com/usuario/proyecto.git
cd proyecto
pip install -r requirements.txt
```

## Uso

Cómo ejecutar la aplicación con uvicorn.

```bash
uvicorn main:app --reload
```

Con Docker compose:

```bash
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d
```

## Configuración

Se requiere los siguientes variables de entorno:

```bash
DATABASE_URL=mysql://user:passwd@host:port/db
SECRET_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_BUCKET_NAME=
HOST=127.0.0.1
PORT=8000
```

## Tecnologías

Lista de tecnologías, frameworks, librerías usadas.

- Python 3.12
- FastAPI
- Docker
- TensorFlow
- Sklearn
- Pandas
- NumPY

## Contribución

¡Gracias por tu interés en contribuir a este proyecto! Para mantener la calidad y coherencia, por favor sigue estos pasos:

1. **Haz un fork** de este repositorio.  
2. **Crea una rama** para tu nueva funcionalidad o corrección:  
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Realiza tus cambios y asegúrate de que el código está bien probado y documentado.**
4. **Haz commit de tus cambios con mensajes claros y descriptivos:**
   ```bash
   git commit -m "Descripción breve del cambio"
   ```
5. **Envía un pull request a la rama _main_ del repositorio original.**

Por favor, asegúrate de que tus contribuciones cumplen con el estilo del código.
