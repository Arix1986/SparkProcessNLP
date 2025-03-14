import pandas as pd
import re
from textblob import TextBlob
from flask import Flask, request, jsonify

app = Flask(__name__)

def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)

    columns_to_keep = [
        'author/id', 'createdAt', 'quoteCount', 'quoteId', 'replyCount', 'retweetCount',
        'source', 'text', 'type',
    ]

    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        print(f"Warning: The following columns are missing: {missing_columns}")
        return None

    df = df[columns_to_keep]

    def clean_text(text):
        if pd.isna(text):
            return text
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.lower()
        return text

    df['cleaned_text'] = df['text'].apply(clean_text)

    df = df.dropna(subset=['cleaned_text'])

    return df

def perform_sentiment_analysis(df):
    def get_sentiment(text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity >= 0:
            return "positive"
        else:
            return "negative"

    df['sentiment'] = df['cleaned_text'].apply(get_sentiment)

    return df

def generate_summary(df):
    sentiment_counts = df['sentiment'].value_counts()

    summary = {
        "positive_count": int(sentiment_counts.get("positive", 0)),
        "negative_count": int(sentiment_counts.get("negative", 0)),
    }

    return summary

@app.route('/process', methods=['POST'])
def process_data():
    df = load_and_clean_data('dataset_nvidia.csv')
    if df is None:
        return jsonify({"error": "Failed to load or clean data"}), 500

    df = perform_sentiment_analysis(df)

    summary = generate_summary(df)

    positive_tweets = df[df['sentiment'] == 'positive'].head(5)
    negative_tweets = df[df['sentiment'] == 'negative'].head(5)

    json_output = {
        "summary": summary,
        "tweets": df[['text', 'sentiment']].to_dict('records'),
        "example_tweets": {
            "positive": positive_tweets[['text', 'sentiment']].to_dict('records'),
            "negative": negative_tweets[['text', 'sentiment']].to_dict('records'),
        }
    }

    return jsonify(json_output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)