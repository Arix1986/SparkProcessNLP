import os
import sys
from flask import Flask, request, jsonify
import pandas as pd
import random
from textblob import TextBlob
import re
import time
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.app_twitter_scraper import TwitterScraper

app = Flask(__name__)

# Development mode flag (True for fake scraping, False for real scraping)
DEVELOPMENT_MODE = True  

# Load fake dataset path (for development mode)
FAKE_DATASET_PATH = "dataset_nvidia.csv"

# Initialize scraper (only used in production mode)
token = os.getenv("APIFY_TOKEN")
scraper = TwitterScraper(token) if token else None

def clean_text(text):
    if pd.isna(text):
        return text
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

def load_and_clean_data(file_path):
    try:
        df = pd.read_csv(file_path)
        columns_to_keep = [
            'author/id', 'createdAt', 'quoteCount', 'quoteId', 'replyCount', 
            'retweetCount', 'source', 'text', 'type'
        ]
        # Filter columns and clean text
        df = df[[col for col in columns_to_keep if col in df.columns]]
        df['cleaned_text'] = df['text'].apply(clean_text)
        df = df.dropna(subset=['cleaned_text'])
        return df
    except Exception as e:
        print(f"Error loading/cleaning data: {e}")
        return None

def perform_sentiment_analysis(df):
    def get_sentiment(text):
        analysis = TextBlob(str(text))
        return "positive" if analysis.sentiment.polarity >= 0 else "negative"

    df['sentiment'] = df['cleaned_text'].apply(get_sentiment)
    return df

def generate_summary(df):
    sentiment_counts = df['sentiment'].value_counts()
    return {
        "positive_count": int(sentiment_counts.get("positive", 0)),
        "negative_count": int(sentiment_counts.get("negative", 0)),
    }

def simulate_scraping(data):
    """Simulate scraping process with delays (for DEVELOPMENT_MODE)."""
    time.sleep(2)  # Simulate scraping delay
    df = load_and_clean_data(FAKE_DATASET_PATH)
    if df is None:
        return None
    return perform_sentiment_analysis(df)

@app.route('/process', methods=['POST'])
def process_tweets():
    data = request.json

    if DEVELOPMENT_MODE:
        # Simulate scraping and analysis
        df = simulate_scraping(data)
        if df is None:
            return jsonify({"error": "Failed to load fake dataset"}), 500

        summary = generate_summary(df)
        example_tweets = {
            "positive": df[df['sentiment'] == 'positive'].head(3)[['text', 'sentiment']].to_dict('records'),
            "negative": df[df['sentiment'] == 'negative'].head(3)[['text', 'sentiment']].to_dict('records'),
        }

        return jsonify({
            "status": "completed",
            "summary": summary,
            "example_tweets": example_tweets,
            "tweets": df[['text', 'sentiment']].to_dict('records')
        })

    else:
        # Real scraping logic
        try:
            output_path = "scraped_tweets.csv"
            scraper.run_scraper(
                search_terms=data.get("search_terms"),
                output_path=output_path,
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                max_items=data.get("max_items", 500),
                tweet_language=data.get("tweet_language", "en"),
                mentioning=data.get("mentioning", ""),
                min_favorites=data.get("min_favorites", 5),
                min_replies=data.get("min_replies", 5),
                min_retweets=data.get("min_retweets", 5),
                only_video=data.get("only_video", False),
                only_verified=data.get("only_verified", False),
                only_image=data.get("only_image", False),
                only_quote=data.get("only_quote", False),
                only_twitter_blue=data.get("only_twitter_blue", False),
                keep_all_response_data=data.get("keep_all_response_data", False),
            )

            df = pd.read_csv(output_path)
            df = perform_sentiment_analysis(df)
            summary = generate_summary(df)

            return jsonify({
                "status": "completed",
                "summary": summary,
                "example_tweets": {
                    "positive": df[df['sentiment'] == 'positive'].head(3)[['text', 'sentiment']].to_dict('records'),
                    "negative": df[df['sentiment'] == 'negative'].head(3)[['text', 'sentiment']].to_dict('records'),
                },
                "tweets": df[['text', 'sentiment']].to_dict('records')
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
