import time
from app_twitter_scraper import TwitterScraper
from datetime import datetime, timedelta

TOKEN = "YOUR_APIFY_KEY"

# Inicializar el scraper
scraper = TwitterScraper(TOKEN)

# Eeventos importantes y sus rangos de fechas
events = [
    {"name": "Q2 2024 Earnings", "date": "2023-08-20"},
    {"name": "Computex DGX GH200", "date": "2023-05-28"},
    {"name": "Microsoft Partnership", "date": "2023-03-21"},
    {"name": "US GPU Export Restrictions", "date": "2022-09-20"},
    {"name": "Arm Holdings Acquisition", "date": "2021-05-01"},
]

# Configuración de parámetros contemplando restricciones del API y para no sobrepasar costos
search_terms = ["NVIDIA", "NVIDIA AI", "GeForce", "RTX", "DGX GH200", "GPU", "NVIDIA Earnings"]
max_items = 1000  # No pasar de este valor
min_favorites = 20  # Filtra tweets con engagement para evitar spam
min_replies = 5
min_retweets = 10
only_verified = False  # Puede activarse si queremos contemplar solo tweets confiables

output_path = "output/tweets_nvidia.csv"

# Iterar sobre cada evento para extraer tweets en las fechas clave
for index, event in enumerate(events):
    # Rango de fechas propuesto: 3 días antes y después del evento
    event_date = datetime.strptime(event["date"], "%Y-%m-%d")
    start_date = (event_date - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = (event_date + timedelta(days=3)).strftime("%Y-%m-%d")

    print(f"Extrayendo tweets para: {event['name']} ({start_date} - {end_date})")

    # Ejecutar el scraper
    scraper.run_scraper(
        search_terms=search_terms,
        output_path=output_path,
        max_items=max_items,
        min_favorites=min_favorites,
        min_replies=min_replies,
        min_retweets=min_retweets,
        only_verified=only_verified,
        start_date=start_date,
        end_date=end_date
    )

    # Si no es el último evento, esperar 5 minutos antes de la siguiente ejecución
    if index < len(events) - 1:
        print("Esperando 5 minutos antes de la siguiente petición...\n\n")
        time.sleep(300)  # Esperar 300 segundos (5 minutos)
