# Frontend - Análisis de Sentimientos de Twitter

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
