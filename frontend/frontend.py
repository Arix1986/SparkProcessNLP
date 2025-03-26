# frontend/frontend.py
from datetime import datetime, date
from api_requests import run_search_tweets
import streamlit as st
import requests
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

# Set page configuration
st.set_page_config(page_title="Twitter Sentiment Analysis", layout="wide")

# Initialize session state
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Function to display the input form
def display_input_form():
    st.title("Twitter Sentiment Analysis Scraper")

    st.header("Input Data")
    keyword = st.text_input("Enter a keyword (e.g., #Python, OpenAI):", value="nvidia")
    start_date = st.date_input("Start date:", value=date(2024, 3, 1))
    end_date = st.date_input("End date:", value=date(2024, 3, 10))

    with st.expander("Advanced Options"):
        max_items = st.number_input("Maximum number of tweets to scrape:", min_value=1, value=10)
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Fake Scrape"):
            st.session_state.show_results = True
            st.session_state.data = {
                "search_terms": [keyword],
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
    with col2:
        if st.button("Scrape Tweets"):
            st.session_state.show_results = True
            st.session_state.data = {
                "search_terms": [keyword],
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

# Function to display the results
def display_results():
    st.title("Scraping Results")

    with st.spinner("Fetching data and performing sentiment analysis..."):
        try:
            # Get results from run_search_tweets
            result = run_search_tweets(**st.session_state.data)

            print(result)

            st.success("Scraping and sentiment analysis completed successfully!")

            # Convert the result to a DataFrame for analysis
            df = pd.DataFrame(result)
            
            # Calculate sentiment summary
            positive_count = len(df[df['predict'] == 1])
            negative_count = len(df[df['predict'] == 0])
            
            st.header("Sentiment Analysis Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Positive Tweets", positive_count)
            with col2:
                st.metric("Negative Tweets", negative_count)

            st.subheader("Sentiment Distribution")
            sentiment_counts = {
                "Positive": positive_count,
                "Negative": negative_count,
            }

            # Create a pie chart using Seaborn
            fig, ax = plt.subplots()
            sns.set_palette("pastel")
            ax.pie(
                sentiment_counts.values(),
                labels=sentiment_counts.keys(),
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 1},
            )
            ax.axis('equal')

            # Display the pie chart on the left half of the screen
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(fig)

            # Display example tweets on the right half of the screen
            with col2:
                st.subheader("Example Tweets")
                positive_examples = df[df['predict'] == 1]
                negative_examples = df[df['predict'] == 0]

                st.write("Positive Tweets:")
                st.dataframe(positive_examples[['text', 'prob']], use_container_width=True)
                st.write("Negative Tweets:")
                st.dataframe(negative_examples[['text', 'prob']], use_container_width=True)

            st.subheader("Download Results")
            json_str = json.dumps(result, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="sentiment_analysis_results.json",
                mime="application/json",
            )
        except Exception as e:
            st.error(f"An error occurred during scraping or sentiment analysis: {str(e)}")

    if st.button("Back to Input"):
        st.session_state.show_results = False

# Main logic
if not st.session_state.show_results:
    display_input_form()
else:
    display_results()