# Twitter Scraper con Apify

## Descripción
Este proyecto es un scraper de Twitter que utiliza la API de **Apify** para extraer tweets relacionados con eventos importantes de NVIDIA. Se ha optimizado para realizar peticiones de manera eficiente, sin sobrepasar costos innecesarios, y guarda los datos en formato CSV con todos los campos obtenidos o campos filtrados.

## Características
- Utiliza **Apify** para la extracción de tweets. Se usa el scrapper [Tweet Scraper V2 (Pay Per Result) - X / Twitter Scraper](https://console.apify.com/actors/61RPP7dywgiy0JPD0/information/latest/readme)
- Filtra tweets con parámetros como número mínimo de **likes, retweets y respuestas**.
- Extrae información de eventos clave de NVIDIA en un rango de **3 días antes y 3 días después**.
- Guarda los datos en formato **CSV**.
- Espera **5 minutos** entre peticiones para optimizar el uso del API de Apify.

## Requisitos
- **Python 3.8+**
- **Apify Client** (`pip install apify-client`)
- **Pandas** (`pip install pandas`)

## Configuración
- **API Token**: Se debe agregar el token de Apify en el script `main.py`.
  ```python
  TOKEN = "tu_apify_api_key"
  ```
- **Eventos a analizar**: Están definidos en la lista `events` en `main.py`. Puedes agregar o modificar eventos según sea necesario.
- **Parámetros de búsqueda**: Se configuran en la variable `search_terms`.

## Uso
Ejecuta el script principal:
```sh
python main.py
```
El scraper buscará tweets de los eventos definidos, guardará los datos en `tweets_nvidia.csv` y esperará **5 minutos entre cada petición**.

## Salida de Datos
El archivo CSV por defecto filtrara los campos obtenidos. Ese listado incluirá las siguientes columnas:
- `url`
- `twitterUrl`
- `text`
- `source`
- `createdAt`
- `possiblySensitive`
- `retweetCount`
- `replyCount`
- `likeCount`
- `quoteCount`
- `bookmarkCount`
- `authorType`
- `authorIsVerified`
- `authorIsBlueVerified`
- `authorFollowers`
- `authorFollowing`

Si el archivo **ya existe**, los nuevos tweets se agregarán al final del documento.

## Ejemplo de Modificación de Fechas
Si deseas modificar el rango de fechas (número de días antes o después), cambia este código en `main.py`:
```python
start_date = (event_date - timedelta(days=3)).strftime("%Y-%m-%d")
end_date = (event_date + timedelta(days=3)).strftime("%Y-%m-%d")
```
Por ejemplo, si quieres **solo tweets del día exacto del evento**, puedes cambiarlo por:
```python
start_date = event_date.strftime("%Y-%m-%d")
end_date = event_date.strftime("%Y-%m-%d")
```

