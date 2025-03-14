import os
import sys
from flask import Flask, request, jsonify

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.app_twitter_scraper import TwitterScraper

app = Flask(__name__)

token = os.getenv("APIFY_TOKEN")
scraper = TwitterScraper(token)

@app.route('/process', methods=['POST'])
def process_tweets():
    data = request.json

    search_terms = data.get("search_terms")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    max_items = data.get("max_items", 500)
    tweet_language = data.get("tweet_language", "en")
    mentioning = data.get("mentioning", "")
    min_favorites = data.get("min_favorites", 5)
    min_replies = data.get("min_replies", 5)
    min_retweets = data.get("min_retweets", 5)
    only_video = data.get("only_video", False)
    only_verified = data.get("only_verified", False)
    only_image = data.get("only_image", False)
    only_quote = data.get("only_quote", False)
    only_twitter_blue = data.get("only_twitter_blue", False)
    keep_all_response_data = data.get("keep_all_response_data", False)

    output_path = "scraped_tweets.csv"
    scraper.run_scraper(
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

    import pandas as pd
    df = pd.read_csv(output_path)

    import random
    sentiments = ['positive', 'negative']
    df['sentiment'] = [random.choice(sentiments) for _ in range(len(df))]

    summary = {
        "positive_count": len(df[df['sentiment'] == 'positive']),
        "negative_count": len(df[df['sentiment'] == 'negative']),
    }

    return jsonify({
        "summary": summary,
        "tweets": df.to_dict(orient="records")
    })

if __name__ == '__main__':
    app.run(debug=True)