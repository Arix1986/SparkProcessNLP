FROM python:3.9-slim

WORKDIR /app

# Copiar y instalar dependencias
COPY backend/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY backend/app/ .

# Copiar el contenido de la carpeta scraper
COPY scraper ./scraper

# Exponer el puerto (FastAPI usará el 8080 en este ejemplo)
EXPOSE 8080

# Comando de inicio (utilizando uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]