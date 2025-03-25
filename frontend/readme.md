# Frontend - Análisis de Sentimientos de Twitter

Video:  [Link a Google Drive](https://drive.google.com/file/d/1ksrJAg3GBKwjYtjWS7p-z5UxODcmP9Sn/view?usp=sharing)

Este repositorio contiene el código del frontend y backend para un sistema de análisis de sentimientos de tweets. El frontend está desarrollado con **Streamlit** y el backend con **Flask**. El backend se comunica con un scraper de Twitter para obtener tweets y realizar un análisis de sentimientos básico.

## Estructura del Proyecto

- **`frontend.py`**: Aplicación de Streamlit que permite al usuario ingresar parámetros para buscar tweets y visualizar los resultados del análisis de sentimientos.
- **`backend.py`**: Servidor Flask que recibe las solicitudes del frontend, ejecuta el scraper de Twitter y realiza un análisis de sentimientos básico.

## Requisitos

Para ejecutar este proyecto, necesitas tener instalado lo siguiente:

- Python 3.8 o superior.
- Las bibliotecas de Python listadas en `requirements.txt`.

### Instalación de Dependencias

1. Clona este repositorio.
2. Navega a la carpeta `frontend`.
3. Instala las dependencias con el siguiente comando:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. **Token de Apify**: Necesitas un token de Apify para utilizar el scraper de Twitter. Asegúrate de configurar la variable de entorno `APIFY_TOKEN` antes de ejecutar el backend.

   ```bash
   export APIFY_TOKEN="tu_token_de_apify_aquí"
   ```

2. **Ejecución del Backend**: El backend debe estar en ejecución para que el frontend funcione correctamente. Para iniciar el servidor Flask, ejecuta:

   ```bash
   python backend.py
   ```

3. **Ejecución del Frontend**: Una vez que el backend esté en ejecución, puedes iniciar la aplicación de Streamlit con:

   ```bash
   streamlit run frontend.py
   ```

## Uso

1. **Interfaz de Usuario**: La interfaz de usuario de Streamlit permite ingresar un término de búsqueda, fechas de inicio y fin, y otros parámetros avanzados para filtrar los tweets.
2. **Análisis de Sentimientos**: Después de hacer clic en "Scrape Tweets", el backend realizará el scraping de los tweets y realizará un análisis de sentimientos básico.
3. **Visualización de Resultados**: Los resultados se mostrarán en la interfaz de Streamlit, incluyendo un resumen del análisis de sentimientos, un gráfico de distribución de sentimientos y ejemplos de tweets positivos y negativos.
4. **Descarga de Resultados**: Los resultados también se pueden descargar en formato JSON.

## Ejemplo de Uso

1. Ingresa un término de búsqueda, como `#Python` o `OpenAI`.
2. Selecciona un rango de fechas.
3. Ajusta los parámetros avanzados si es necesario.
4. Haz clic en "Scrape Tweets".
5. Visualiza los resultados en la interfaz de Streamlit.


## Puntos Clave de Integración

### 🔧 Variables de Configuración (Revisar antes de desplegar)
backend.py
```python backend.py
DEVELOPMENT_MODE = True  # Cambiar a False para scraping real
FAKE_DATASET_PATH = "dataset_nvidia.csv"  # Datos de prueba
APIFY_TOKEN = os.getenv("APIFY_TOKEN")  # Necesario para producción

# En frontend.py
BACKEND_URL = "http://localhost:5000/process"  # Actualizar en producción
```

### 🔄 Flujo de Datos
Frontend (Streamlit) → [JSON] → Backend (Flask) → [Scraper/NLP] → → [Respuesta JSON] → Frontend (Visualización)


### 📦 Estructura de Comunicación
**Frontend → Backend (POST /process)**
```json
{
  "search_terms": "#Python",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "max_items": 500,
  "tweet_language": "es",
  "min_favorites": 5
}
Backend → Frontend (Respuesta)

{
  "status": "completed",
  "summary": {
    "positive_count": 120,
    "negative_count": 80
  },
  "example_tweets": {
    "positive": [{"text": "Me encanta programar!", "sentiment": "positive"}],
    "negative": [{"text": "No me gusta programar", "sentiment": "negative"}]
  }
}
```

## ⚙️ Funciones Críticas
Procesamiento en Backend 

backend.py
```python
@app.route('/process', methods=['POST'])
def process_tweets():
    # 1. Recibir datos del frontend
    data = request.json
    
    # 2. Modo desarrollo vs producción
    if DEVELOPMENT_MODE:
        df = simulate_scraping(data)  # Usa FAKE_DATASET_PATH
    else:
        df = real_scrape(data)  # Requiere APIFY_TOKEN
    
    # 3. Análisis de sentimientos
    df = perform_sentiment_analysis(df)
    
    # 4. Formatear respuesta
    return jsonify({
        "summary": generate_summary(df),
        "example_tweets": extract_examples(df)
    })
```

Manejo en Frontend 

frontend.py

```python
def display_results():
    # 1. Enviar solicitud al backend
    response = requests.post(BACKEND_URL, json=st.session_state.data)
    
    # 2. Procesar respuesta
    if response.status_code == 200:
        result = response.json()
        show_metrics(result['summary'])
        show_chart(result['summary'])
        show_examples(result['example_tweets'])

```
🚀 Checklist para Despliegue
Modo Desarrollo:

Mantener DEVELOPMENT_MODE = True
Asegurar que dataset_nvidia.csv exista
No se requiere token de API
Modo Producción:

Cambiar DEVELOPMENT_MODE = False
Configurar variable de entorno APIFY_TOKEN
Actualizar BACKEND_URL si se despliega remotamente
Para Escalar:

Para muchos tweets (>1k), aumentar timeout:

backend.py

app.run(debug=True, threaded=True, timeout=600)
Considerar usar Redis para procesamiento asíncrono
🔗 Conexión con otros Componentes
# Para integrar con NLP:

Modificar:
```python
perform_sentiment_analysis()
 en 
backend.py
 para:
Llamara servicio NLP en lugar de TextBlob
Mantener la misma estructura de respuesta:
{
    "sentiment": "positive"|"negative",
    "text": "texto original"
}
```

Ejemplo de integración:

backend.py

```python
# Reemplazar TextBlob con modelo
def get_sentiment(text):
    # Llamar al modelo NLP aquí
    return nlp_model.predict(text)
```
📊 Estructura de Datos
Columnas requeridas en CSV para modo desarrollo:

```
author/id,createdAt,text,quoteCount,replyCount,retweetCount
```

🛠 Solución de Problemas
Errores de conexión: Verificar que BACKEND_URL coincida
Resultados vacíos: Revisar logs del scraper
Lentitud: Reducir max_items en el formulario
