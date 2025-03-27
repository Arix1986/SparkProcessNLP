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
token = os.getenv("APIFY_TOKEN")
scraper = TwitterScraper(token) if token else None

# Get the current directory path and create output directory
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

async def search_tweets(search_terms, start_date, end_date, max_items=10, tweet_language="en", 
                    mentioning="",  min_favorites=5, min_replies=5, min_retweets=5, only_video=False,
                    only_verified=False, only_image=False, only_quote=False, only_twitter_blue=False,
                    keep_all_response_data=False):
    try:
        output_path = os.path.join(output_dir, "scraped_tweets.csv")        
        
        # Run scraper
        await scraper.run_scraper(
            search_terms=search_terms,
            output_path=output_path,
            start_date=start_date,
            end_date=end_date,
            max_items=max_items,
            tweet_language=tweet_language,
            mentioning=mentioning,
            min_favorites=min_favorites,
            min_replies=min_replies,
            min_retweets=min_retweets,
            only_video=only_video,
            only_verified=only_verified,
            only_image=only_image,
            only_quote=only_quote,
            only_twitter_blue=only_twitter_blue,
            keep_all_response_data=keep_all_response_data,
        )

        # Read the CSV file
        df = pd.read_csv(output_path)
        df = df[['text']]
        df.to_csv(os.path.join(output_dir, "scraped_tweets_text.csv"), index=False)

        # Use aiohttp for async HTTP requests
        async with aiohttp.ClientSession() as session:
            # First request to upload file
            with open(os.path.join(output_dir, "scraped_tweets_text.csv"), "rb") as f:
                data = aiohttp.FormData()
                data.add_field('file', f)
                async with session.post("http://34.16.65.91:5000/get_test_file", data=data) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to get summary: {response.status} - {await response.text()}")
                    
                    response_data = await response.json()
                    file_path = response_data.get("path")

                    # Second request for inference
                    inference_payload = {
                        "path": file_path,
                        "tipo": "csv"
                    }
                    async with session.post(
                        "http://34.16.65.91:5000/inferencia",
                        headers={"accept": "application/json", "Content-Type": "application/json"},
                        json=inference_payload
                    ) as inference_response:
                        if inference_response.status != 200:
                            raise Exception(f"Failed to get inference: {inference_response.status} - {await inference_response.text()}")
                        
                        inference_data = await inference_response.json()
                        if not inference_data:
                            raise Exception("Failed to get inference data")

                        # Add predict and prob columns to the df
                        for i, item in enumerate(inference_data):
                            df.loc[i, 'predict'] = item['predict']
                            df.loc[i, 'prob'] = item['prob']

                        # Clean up temporary files
                        os.remove(os.path.join(output_dir, "scraped_tweets_text.csv"))
                        os.remove(os.path.join(output_dir, "scraped_tweets.csv"))

                        return df.to_dict('records')

    except Exception as e:
        print(e)
        raise e

# Wrapper function to run the async function
def run_search_tweets(*args, **kwargs):
    return asyncio.run(search_tweets(*args, **kwargs))