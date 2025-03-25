# Documentación del API Backend

Este es el servicio backend API construido con FastAPI que proporciona capacidades de procesamiento NLP.

## Prerrequisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Docker (opcional, para despliegue en contenedores)

## Configuración del Entorno Local

1. Crear y activar un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
cd app
pip install -r requirements.txt
```

3. Configurar variables de entorno:
- Copiar el archivo `.env.example` a `.env` (si está disponible)
- Configurar las variables de entorno requeridas

4. Ejecutar el API localmente:
```bash
uvicorn main:app --reload --port 8080
```

El API estará disponible en `http://localhost:8080`

## Despliegue con Docker

1. Construir la imagen Docker:
```bash
docker build -t spark-process-nlp-backend .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8080:8080 --env-file .env spark-process-nlp-backend
```

El API estará disponible en `http://localhost:8080`

## Documentación del API

Una vez que el API esté en ejecución, puedes acceder a:
- Documentación interactiva del API (Swagger UI): `http://localhost:8080/docs`
- Documentación alternativa del API (ReDoc): `http://localhost:8080/redoc`

## Notas de Desarrollo

- El API utiliza el framework FastAPI con Uvicorn como servidor ASGI
- Las variables de entorno se gestionan a través de python-dotenv
- La estructura de la aplicación sigue un diseño modular con componentes separados para diferentes funcionalidades

## Solución de Problemas

1. Si encuentras conflictos de puertos:
   - Cambia el número de puerto en el comando de ejecución
   - Actualiza el mapeo de puertos en Docker si estás usando despliegue en contenedores

2. Para problemas con dependencias:
   - Asegúrate de estar usando Python 3.9 o superior
   - Intenta recrear el entorno virtual
   - Verifica que todas las dependencias estén correctamente instaladas

3. Para problemas relacionados con Docker:
   - Asegúrate de que el daemon de Docker esté en ejecución
   - Verifica que el puerto no esté siendo utilizado por otros servicios
   - Comprueba que el archivo .env esté correctamente configurado 