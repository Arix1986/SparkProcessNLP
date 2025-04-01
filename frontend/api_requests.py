import os
import sys
import pandas as pd
import asyncio
import aiohttp
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from scraper.app_twitter_scraper import TwitterScraper

# Initialize scraper
token = "apify_api_XmzodU8QoayHLTBPkws22kC2GiLsR700gVm3" #os.getenv("APIFY_TOKEN")
scraper = TwitterScraper(token) if token else None

BACKEND_URL="http://34.59.29.99:5000"

# Get the current directory path and create output directory
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

async def scrape_and_prepare_csv(data):
    output_path = os.path.join(output_dir, "scraped_tweets.csv")
    
    await scraper.run_scraper(output_path=output_path, **data)
    
    df = pd.read_csv(output_path)
    df = df[['text']]
    text_csv_path = os.path.join(output_dir, "scraped_tweets_text.csv")
    df.to_csv(text_csv_path, index=False)
    
    return text_csv_path, df

async def upload_file_and_predict(text_csv_path):
    async with aiohttp.ClientSession() as session:
        print("Uploading file...", text_csv_path)
        with open(text_csv_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field('file', f)
            async with session.post(BACKEND_URL+"/get_test_file", data=data) as response:
                response_data = await response.json()
                file_path = response_data.get("path")
        
        print("Getting predictions..." + file_path)
        inference_payload = {"path": file_path, "tipo": "csv"}
        async with session.post(
            BACKEND_URL+"/inferencia",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=inference_payload
        ) as inference_response:
            inference_response.raise_for_status()  # Raise exception for bad status codes
            inference_data = await inference_response.json()
            print("Inference response data:", inference_data)
            return inference_data

def run_analysis_steps(data):
    async def _run():
        path, df = await scrape_and_prepare_csv(data)
        predictions = await upload_file_and_predict(path)
        for i, item in enumerate(predictions):
            df.loc[i, 'predict'] = item['predict']
            df.loc[i, 'prob'] = item['prob']
        os.remove(path)
        os.remove(os.path.join(output_dir, "scraped_tweets.csv"))
        return df.to_dict('records')
    
    return asyncio.run(_run())