# Frontend - Análisis de Sentimientos de Twitter

Este repositorio contiene el código del frontend y la comunicación con el backend para un sistema de análisis de sentimientos de tweets. El frontend está desarrollado con **Streamlit** y utiliza **`aiohttp`** para interactuar con un scraper externo implementado con **APIFY** y un backend de análisis de sentimientos.

## 🧠 ¿Cómo funciona?

1. El usuario ingresa términos de búsqueda y filtros desde una interfaz web.
2. El scraper de Twitter (vía APIFY) recupera los tweets.
3. El backend procesa los textos con un modelo de análisis de sentimientos.
4. El frontend visualiza resultados y permite exportar los datos.

## Requisitos

Para ejecutar este proyecto, necesitas tener instalado lo siguiente:

- Python 3.12.9 o superior
- Conda (para gestión de entornos virtuales)
- Las bibliotecas de Python listadas en `../requirements.txt`

### Instalación con Conda (Recomendado)

1. Asegúrate de tener Conda instalado en tu sistema
2. Ubícate en la raíz del proyecto **SparkProcessNLP**
3. Ejecuta los siguientes comandos en tu terminal:

```bash
# Crear el entorno virtual con Conda
conda create -n sparknlp_base python=3.12.9 -y

# Activar el entorno e instalar dependencias
conda activate sparknlp_base && pip install -r requirements.txt

# Ejecutar la aplicación
conda activate sparknlp_base && streamlit run frontend/0_Input_Form.py

# Para desactivar el entorno cuando termines
conda deactivate

# Para ver la lista de entornos
conda env list

# Para eliminar el entorno si ya no lo necesitas
conda remove -n sparknlp_base --all
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


### 🔄 Flujo de Datos
Frontend (Streamlit) → [JSON] → Backend (APIFY) → [Scraper/NLP] → → [Respuesta JSON] → Frontend (Visualización)
