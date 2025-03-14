import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

st.title("Twitter Sentiment Analysis Scraper")

st.header("Input Data")
keyword = st.text_input("Enter a keyword (e.g., #Python, OpenAI):")
start_date = st.date_input("Start date:")
end_date = st.date_input("End date:")

with st.expander("Advanced Options"):
    max_items = st.number_input("Maximum number of tweets to scrape:", min_value=1, value=500)
    tweet_language = st.text_input("Tweet Language (e.g., 'en' for English):", value="en")
    mentioning = st.text_input("Mentioning (comma-separated usernames):", value="")
    min_favorites = st.number_input("Minimum Favorites:", min_value=0, value=5)
    min_replies = st.number_input("Minimum Replies:", min_value=0, value=5)
    min_retweets = st.number_input("Minimum Retweets:", min_value=0, value=5)
    only_video = st.checkbox("Only Video Tweets", value=False)
    only_verified = st.checkbox("Only Verified Users", value=False)
    only_image = st.checkbox("Only Image Tweets", value=False)
    only_quote = st.checkbox("Only Quote Tweets", value=False)
    only_twitter_blue = st.checkbox("Only Twitter Blue Users", value=False)
    keep_all_response_data = st.checkbox("Keep All Response Data", value=False)

if st.button("Fake Scrape"):
    try:
        response = requests.post("http://localhost:5000/process", json={})
        
        if response.status_code == 200:
            result = response.json()

            st.success("Fake scraping and sentiment analysis completed successfully!")

            st.header("Sentiment Analysis Summary")
            st.write(f"Positive Tweets: {result['summary']['positive_count']}")
            st.write(f"Negative Tweets: {result['summary']['negative_count']}")

            st.subheader("Sentiment Distribution")
            sentiment_counts = {
                "Positive": result['summary']['positive_count'],
                "Negative": result['summary']['negative_count'],
            }
            
            fig, ax = plt.subplots()
            ax.pie(
                sentiment_counts.values(),
                labels=sentiment_counts.keys(),
                autopct='%1.1f%%',
                colors=['green', 'red'],
                startangle=90,
            )
            ax.axis('equal')
            st.pyplot(fig)

            st.subheader("Example Tweets")
            positive_examples = pd.DataFrame(result['example_tweets']['positive'])
            negative_examples = pd.DataFrame(result['example_tweets']['negative'])

            st.write("Positive Tweets:")
            st.table(positive_examples)
            st.write("Negative Tweets:")
            st.table(negative_examples)

            st.subheader("Download Results")
            json_str = json.dumps(result, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="sentiment_analysis_results.json",
                mime="application/json",
            )
        else:
            st.error("Failed to fetch data from the backend.")
    
    except Exception as e:
        st.error(f"An error occurred during fake scraping: {str(e)}")

if st.button("Scrape Tweets"):
    data = {
        "search_terms": keyword,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "max_items": max_items,
        "tweet_language": tweet_language,
        "mentioning": mentioning,
        "min_favorites": min_favorites,
        "min_replies": min_replies,
        "min_retweets": min_retweets,
        "only_video": only_video,
        "only_verified": only_verified,
        "only_image": only_image,
        "only_quote": only_quote,
        "only_twitter_blue": only_twitter_blue,
        "keep_all_response_data": keep_all_response_data,
    }

    response = requests.post("http://localhost:5000/process", json=data)

    if response.status_code == 200:
        st.success("Scraping and sentiment analysis completed successfully!")
        result = response.json()

        st.header("Sentiment Analysis Summary")
        st.write(f"Positive Tweets: {result['summary']['positive_count']}")
        st.write(f"Negative Tweets: {result['summary']['negative_count']}")

        st.subheader("Sentiment Distribution")
        sentiment_counts = {
            "Positive": result['summary']['positive_count'],
            "Negative": result['summary']['negative_count'],
        }
        fig, ax = plt.subplots()
        ax.pie(
            sentiment_counts.values(),
            labels=sentiment_counts.keys(),
            autopct='%1.1f%%',
            colors=['green', 'red'],
            startangle=90,
        )
        ax.axis('equal')
        st.pyplot(fig)

        st.subheader("Example Tweets")
        positive_examples = pd.DataFrame(result['example_tweets']['positive'])
        negative_examples = pd.DataFrame(result['example_tweets']['negative'])

        st.write("Positive Tweets:")
        st.table(positive_examples)
        st.write("Negative Tweets:")
        st.table(negative_examples)

        st.subheader("Download Results")
        json_str = json.dumps(result, indent=4)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="sentiment_analysis_results.json",
            mime="application/json",
        )

    else:
        st.error("An error occurred during scraping or sentiment analysis.")
