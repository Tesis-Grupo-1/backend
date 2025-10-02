# Sistema de Detección de Plagas con Autenticación JWT

## Descripción

Sistema completo de detección de plagas agrícolas con autenticación JWT, roles de usuario (empleado/jefe), gestión de campos, reportes con IA y exportación a PDF.

## Características Principales

### 🔐 Autenticación y Autorización
- **JWT (JSON Web Tokens)** para autenticación segura
- **Roles de usuario**: Empleado y Jefe
- **Cifrado de datos sensibles** (teléfono, dirección, coordenadas, notas)
- **Sistema de códigos únicos** para vincular empleados con jefes

### 👥 Gestión de Usuarios
- **Jefe**: Puede tener múltiples empleados, generar códigos de vinculación, ver reportes de empleados
- **Empleado**: Puede realizar inspecciones, generar reportes, vincularse a un jefe
- **Relación uno a muchos**: Un jefe puede tener varios empleados, un empleado solo un jefe

### 🌾 Gestión de Campos
- **Registro de campos** con tamaño en hectáreas
- **Coordenadas GPS cifradas** para ubicación precisa
- **Descripción detallada** de cada campo

### 🔍 Detección de Plagas
- **Detección automática** usando Roboflow
- **Coordenadas GPS** de la detección
- **Porcentaje de campo afectado** por plaga
- **Notas adicionales** cifradas
- **Historial completo** de detecciones por usuario

### 📊 Reportes con IA
- **Generación automática** usando Gemini AI
- **Análisis técnico** de la situación
- **Recomendaciones** basadas en datos
- **Exportación a PDF** con formato profesional

## Estructura del Proyecto

```
app/
├── api/
│   ├── auth/           # Endpoints de autenticación
│   ├── fields/         # Endpoints de gestión de campos
│   ├── reports/        # Endpoints de reportes
│   └── detection/      # Endpoints de detección
├── models/             # Modelos de base de datos
├── schemas/            # Esquemas de validación
├── services/           # Lógica de negocio
└── core/              # Configuración
```

## Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia `env_example.txt` a `.env` y configura las variables:

```bash
cp env_example.txt .env
```

### 3. Generar clave de cifrado
```bash
python generate_encryption_key.py
```

### 4. Inicializar base de datos
```bash
python init_database.py
```

### 5. Ejecutar servidor
```bash
python main.py
```

## API Endpoints

### Autenticación (`/auth`)
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Inicio de sesión
- `GET /auth/me` - Información del usuario actual
- `PUT /auth/me` - Actualizar perfil
- `POST /auth/link-employee` - Vincular empleado con jefe
- `GET /auth/employees` - Listar empleados (solo jefes)
- `GET /auth/boss` - Información del jefe (solo empleados)
- `POST /auth/regenerate-linking-code` - Regenerar código de vinculación
- `GET /auth/linking-code` - Obtener código de vinculación

### Campos (`/fields`)
- `POST /fields/` - Crear campo
- `GET /fields/` - Listar campos del usuario
- `GET /fields/{field_id}` - Obtener campo específico
- `PUT /fields/{field_id}` - Actualizar campo
- `DELETE /fields/{field_id}` - Eliminar campo
- `GET /fields/boss/employees` - Campos de empleados (solo jefes)

### Detecciones (`/detection`)
- `POST /detection/create` - Crear detección
- `GET /detection/` - Historial de detecciones
- `GET /detection/{detection_id}` - Obtener detección específica
- `PUT /detection/{detection_id}` - Actualizar detección
- `DELETE /detection/{detection_id}` - Eliminar detección
- `GET /detection/boss/employees` - Detecciones de empleados (solo jefes)
- `POST /detection/detect-pests` - Detectar plagas en imagen
- `POST /detection/save_detection` - Guardar detección (legacy)

### Reportes (`/reports`)
- `POST /reports/` - Crear reporte manual
- `POST /reports/generate-ai` - Generar reporte con IA
- `GET /reports/` - Listar reportes del usuario
- `GET /reports/{report_id}` - Obtener reporte específico
- `PUT /reports/{report_id}` - Actualizar reporte
- `DELETE /reports/{report_id}` - Eliminar reporte
- `POST /reports/{report_id}/export-pdf` - Exportar a PDF
- `GET /reports/boss/employees` - Reportes de empleados (solo jefes)

## Flujo de Trabajo

### 1. Registro y Vinculación
1. **Jefe** se registra y obtiene código de vinculación
2. **Empleado** se registra y usa código para vincularse al jefe
3. **Jefe** puede ver y gestionar sus empleados

### 2. Gestión de Campos
1. **Empleado** registra campos con coordenadas GPS
2. **Jefe** puede ver campos de todos sus empleados

### 3. Detección de Plagas
1. **Empleado** sube imagen y ejecuta detección
2. Sistema calcula porcentaje de campo afectado
3. Se guardan coordenadas GPS y notas
4. **Jefe** puede ver todas las detecciones de empleados

### 4. Generación de Reportes
1. **Empleado** genera reporte con IA usando datos de detección
2. Gemini AI analiza situación y genera recomendaciones
3. Reporte se exporta a PDF
4. **Jefe** puede ver todos los reportes de empleados

## Seguridad

### Cifrado de Datos
- **Coordenadas GPS** cifradas en base de datos
- **Notas y descripciones** cifradas
- **Información personal** (teléfono, dirección) cifrada
- **Contenido de reportes** cifrado

### Autenticación JWT
- **Tokens seguros** con expiración configurable
- **Verificación de roles** en cada endpoint
- **Protección de rutas** según permisos de usuario

### Validación de Datos
- **Esquemas Pydantic** para validación
- **Verificación de propiedad** de recursos
- **Sanitización de entradas** de usuario

## Tecnologías Utilizadas

- **FastAPI** - Framework web moderno
- **Tortoise ORM** - ORM asíncrono para Python
- **JWT** - Autenticación basada en tokens
- **Cryptography** - Cifrado de datos sensibles
- **Gemini AI** - Generación de reportes inteligentes
- **ReportLab** - Generación de PDFs
- **Roboflow** - Detección de plagas con IA
- **MySQL** - Base de datos relacional

## Variables de Entorno Requeridas

```env
# Base de datos
DATABASE_URL=mysql://usuario:contraseña@localhost:3306/minascan

# AWS S3 (para almacenamiento de imágenes)
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=tu_bucket_name

# JWT
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000

# Gemini AI
GEMINI_API_KEY=tu_api_key_de_gemini

# Cifrado
ENCRYPTION_KEY=tu_clave_de_cifrado_base64
```

## Usuarios de Ejemplo

Después de ejecutar `init_database.py`:

- **Jefe**: `jefe_ejemplo` / `password123`
- **Empleado**: `empleado_ejemplo` / `password123`

## Notas Importantes

1. **Cifrado**: Todos los datos sensibles están cifrados en la base de datos
2. **Roles**: Los jefes pueden ver datos de empleados, pero no modificarlos
3. **IA**: Los reportes se generan automáticamente usando Gemini AI
4. **PDF**: Los reportes se pueden exportar a PDF con formato profesional
5. **Coordenadas**: Se requieren coordenadas GPS para cada detección
6. **Porcentaje**: Se calcula automáticamente el porcentaje de campo afectado

## Soporte

Para soporte técnico o consultas sobre el sistema, contactar al equipo de desarrollo.
