# 0_Input_Form.py
import streamlit as st
from datetime import date

st.set_page_config(page_title="Twitter Sentiment Analysis", layout="wide")

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

if st.button("Scrape Tweets"):
    st.session_state.data = {
        "search_terms": keyword.split(","),
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

    st.switch_page("pages/1_Results.py")
