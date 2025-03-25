FROM python:3.9-slim

WORKDIR /app

# Copiar y instalar dependencias
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ .

# Exponer el puerto (FastAPI usará el 8080 en este ejemplo)
EXPOSE 8080

# Comando de inicio (utilizando uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]