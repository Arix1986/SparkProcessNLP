import pandas as pd
import os
from apify_client import ApifyClient
from datetime import datetime
import asyncio

class TwitterScraper:
    def __init__(self, token):
        self.client = ApifyClient(token)

    async def run_scraper(self, search_terms, output_path, start_date, end_date, max_items=500, tweet_language="en", 
                    mentioning="",  min_favorites=5, min_replies=5, min_retweets=5, only_video=False,
                    only_verified=False, only_image=False, only_quote=False, only_twitter_blue=False,
                    keep_all_response_data=False):
        
        if mentioning:
            if isinstance(mentioning, list):
                mentioning = ", ".join(mentioning)
        
        # Configurar el input para el scraper
        run_input = {
            "searchTerms": search_terms,
            "maxItems": max_items,
            "includeSearchTerms": True,
            "sort": "Latest",
            "tweetLanguage": tweet_language,
            "mentioning": mentioning,
            "minimumFavorites": min_favorites,
            "minimumReplies": min_replies,
            "minimumRetweets": min_retweets,
            "onlyVerifiedUsers": only_verified,
            "onlyImage": only_image,
            "onlyQuote": only_quote,
            "onlyTwitterBlue": only_twitter_blue,
            "onlyVideo": only_video,
            "start": start_date,
            "end": end_date,
            "customMapFunction": "(object) => { return {...object} }",
        }

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Ejecutando scraper para {search_terms} con {max_items} tweets...")

        # Ejecutar el actor en Apify
        run = self.client.actor("61RPP7dywgiy0JPD0").call(run_input=run_input)

        # Obtener resultados
        data = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        print(f"Datos obtenidos: {len(data)}")

        # Filtrar resultados sin datos
        data = [item for item in data if not item.get('noResults', False)]

        if data:
            if keep_all_response_data: 
                await self.save_to_csv(data, output_path)
            else:
                await self.save_needed_fields_to_csv(data, output_path)
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: No se encontraron datos en la consulta.")

    async def save_to_csv(self, data, output_path):
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Datos guardados en {output_path} - {len(df)} tweets.")
    
    async def save_needed_fields_to_csv(self, data, output_path):
        processed_data = []

        for item in data:
            processed_data.append({
                "url": item.get("url"),
                "twitterUrl": item.get("twitterUrl"),
                "text": item.get("text"),
                "source": item.get("source"),
                "createdAt": item.get("createdAt"),
                "possiblySensitive": item.get("possiblySensitive"),
                "retweetCount": item.get("retweetCount"),
                "replyCount": item.get("replyCount"),
                "likeCount": item.get("likeCount"),
                "quoteCount": item.get("quoteCount"),
                "bookmarkCount": item.get("bookmarkCount"),
                "authorType": item.get("author", {}).get("type"),
                "authorIsVerified": item.get("author", {}).get("isVerified"),
                "authorIsBlueVerified": item.get("author", {}).get("isBlueVerified"),
                "authorFollowers": item.get("author", {}).get("followers"),
                "authorFollowing": item.get("author", {}).get("following"),
            })

        df_new = pd.DataFrame(processed_data)

        # Si el archivo ya existe, cargarlo y agregar los nuevos datos
        if os.path.exists(output_path):
            df_existing = pd.read_csv(output_path, encoding="utf-8")
            df_combined = pd.concat([df_existing, df_new])  # Concatenar
        else:
            df_combined = df_new  # Si no existe, usar solo los nuevos tweets

        # Guardar el archivo CSV
        df_combined.to_csv(output_path, index=False, encoding="utf-8")

        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Datos guardados en {output_path} - {len(df_combined)} tweets.")