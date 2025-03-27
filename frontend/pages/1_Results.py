# pages/1_Results.py
import streamlit as st
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from api_requests import run_search_tweets

st.set_page_config(page_title="Scraping Results", layout="wide")

if 'data' not in st.session_state:
    st.error("No input data found. Please go back and enter search parameters.")
    st.stop()

if 'skip_analysis' not in st.session_state:
    st.session_state.skip_analysis = False

# 👇 Botón para volver al input
if st.button("Back to Input"):
    st.session_state.skip_analysis = True
    st.session_state.data = None
    st.session_state.result = None
    st.session_state.json_str = None
    st.switch_page("0_Input_Form.py")

# 👇 Evita re-ejecutar scraping si ya se hizo
if not st.session_state.skip_analysis:
    st.title("Scraping Results")

    if 'result' not in st.session_state or st.session_state.result is None:
        with st.spinner("Fetching data and performing sentiment analysis..."):
            try:
                result = run_search_tweets(**st.session_state.data)
                st.session_state.result = result
                st.session_state.json_str = json.dumps(result, indent=4)
            except Exception as e:
                st.error(f"An error occurred during scraping or sentiment analysis: {str(e)}")
                st.stop()

    result = st.session_state.result
    df = pd.DataFrame(result)
    positive_count = len(df[df['predict'] == 1])
    negative_count = len(df[df['predict'] == 0])

    st.header("Sentiment Analysis Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Positive Tweets", positive_count)
    with col2:
        st.metric("Negative Tweets", negative_count)

    st.subheader("Sentiment Distribution")
    sentiment_counts = {"Positive": positive_count, "Negative": negative_count}
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
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig)
    with col2:
        st.subheader("Example Tweets")
        st.write("Positive Tweets:")
        st.dataframe(df[df['predict'] == 1][['text', 'prob']], use_container_width=True)
        st.write("Negative Tweets:")
        st.dataframe(df[df['predict'] == 0][['text', 'prob']], use_container_width=True)

    # 👇 Este botón ya no reejecuta scraping
    st.subheader("Download Results")
    st.download_button(
        label="Download JSON",
        data=st.session_state.json_str,
        file_name="sentiment_analysis_results.json",
        mime="application/json",
    )
