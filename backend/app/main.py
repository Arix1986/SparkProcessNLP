import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from dotenv import load_dotenv
from scraper.app_twitter_scraper import TwitterScraper
# from app_text_pprocessor import TextCleaner

# Load environment variables
load_dotenv()

# Get API token from environment variable
apify_token = os.getenv('APIFY_API_TOKEN')
if not apify_token:
    raise ValueError("APIFY_API_TOKEN environment variable is not set")

scraper = TwitterScraper(apify_token)

app = FastAPI()

# Definir modelo de datos
class SearchRequest(BaseModel):
    search_terms: List[str]
    start_date: date
    end_date: date
    max_items: Optional[int] = Field(500, ge=1, le=500)
    tweet_language: Optional[str] = "en"
    mentioning: Optional[str] = ""
    min_favorites: Optional[int] = Field(5, ge=0)
    min_replies: Optional[int] = Field(5, ge=0)
    min_retweets: Optional[int] = Field(5, ge=0)
    only_video: Optional[bool] = False
    only_verified: Optional[bool] = False
    only_image: Optional[bool] = False
    only_quote: Optional[bool] = False
    only_twitter_blue: Optional[bool] = False
    keep_all_response_data: Optional[bool] = False

@app.post("/search")
def search_tweets(request: SearchRequest):
    try:
        # df = scraper.run_scraper(
        #   search_terms=request.search_terms,
        #   output_path="output/tweets_nvidia.csv",
        #   start_date=request.start_date,
        #   end_date=request.end_date,
        #   max_items=request.max_items,
        #   tweet_language=request.tweet_language,
        #   mentioning=request.mentioning,
        #   min_favorites=request.min_favorites,
        #   min_replies=request.min_replies,
        #   min_retweets=request.min_retweets,
        #   only_video=request.only_video,
        #   only_verified=request.only_verified,
        #   only_image=request.only_image,
        #   only_quote=request.only_quote,
        #   only_twitter_blue=request.only_twitter_blue,
        #   keep_all_response_data=request.keep_all_response_data,
        #   return_df=True
        # )

        # # Procesar DF
        # origin_df = df[['text']]
        # print(origin_df.head())
        # cleaner = TextCleaner(spark, use_lemma=True, use_stop_words=True, expand_contractions=True)
        # cleaned_df = cleaner.clean_dataframe(origin_df)

        # Preparar respuesta
        response = {
            "message": "Búsqueda procesada correctamente",
            "results": []
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")