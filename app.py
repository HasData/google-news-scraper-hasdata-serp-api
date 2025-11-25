import streamlit as st
import requests
import json
import pandas as pd
import io

st.set_page_config(page_title="Google News Scraper", layout="wide")

st.markdown("<h1 style='text-align: center;'>Google News Scraping with HasData Google SERP API</h1>", unsafe_allow_html=True)

api_key = st.text_input("Enter your HasData's API Key", placeholder="Your API Key here")

col1, col2 = st.columns([1, 1], gap="small")

with col1:
    search_query = st.text_input("Enter search term", placeholder="e.g., technology")
    pages_to_scrape = st.slider("Number of pages to scrape", min_value=1, max_value=10, value=1)
    start_page = st.slider("Start page", min_value=1, max_value=10, value=1)


with col2:
    time_filter = st.selectbox(
        "Filter by Time",
        ["None", "Past Hour", "Past Day", "Past Week", "Past Month", "Past Year"],
        index=0,
        help="Select a time range to limit the search results"
    )
    language = st.selectbox("Select language", ["English", "Spanish", "French", "German"], index=0)
    lang_map = {"English": "en", "Spanish": "es", "French": "fr", "German": "de"}

    country = st.selectbox("Select country", ["USA", "UK", "Germany", "France", "India"], index=0)
    country_map = {"USA": "us", "UK": "uk", "Germany": "de", "France": "fr", "India": "in"}

time_map = {
    "None": "",
    "Past Hour": "qdr:h",
    "Past Day": "qdr:d",
    "Past Week": "qdr:w",
    "Past Month": "qdr:m",
    "Past Year": "qdr:y"
}

params = {
    "q": search_query,
    "domain": "google.com",
    "gl": country_map[country],
    "hl": lang_map[language],
    "filter": 1,
    "nfpr": 0,
    "tbm": "nws",
    "deviceType": "desktop"
}

if time_map[time_filter]:
    params["tbs"] = time_map[time_filter]

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

if "news_items" not in st.session_state:
    st.session_state.news_items = []

if st.button("Scrape News") and api_key:
    news_items = []
    progress_bar = st.progress(0)
    for page in range(pages_to_scrape):
        params["start"] = ((start_page - 1) + page) * 10
        response = requests.get("https://api.hasdata.com/scrape/google/serp", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("newsResults", []):
                news_items.append({
                    "Row Number": len(news_items) + 1,
                    "Title": item.get("title"),
                    "Link": item.get("link"),
                    "Source": item.get("source"),
                    "Snippet": item.get("snippet"),
                    "Date": item.get("date"),
                    "Thumbnail": item.get("thumbnail")
                })
            progress_bar.progress((page + 1) / pages_to_scrape)
        else:
            st.error(f"Error fetching page {page + 1}: {response.status_code}")
            break
    if news_items:
        st.session_state.news_items = news_items
        df_display = pd.DataFrame(news_items).drop(columns=["Row Number"], errors="ignore")
        st.write(df_display)
        json_data = json.dumps(news_items, ensure_ascii=False, indent=2)
        csv_buffer = io.StringIO()
        pd.DataFrame(news_items).to_csv(csv_buffer, index=False)
        col3, col4 = st.columns([1, 1], gap="small")
        with col3:
            st.download_button("Download JSON", data=json_data, file_name="news.json", mime="application/json")
        with col4:
            st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="news.csv", mime="text/csv")

    else:
        st.warning("No data found.")
elif st.session_state.news_items:
    df_display = pd.DataFrame(st.session_state.news_items).drop(columns=["Row Number"], errors="ignore")
    st.write(df_display)
    json_data = json.dumps(st.session_state.news_items, ensure_ascii=False, indent=2)
    csv_buffer = io.StringIO()
    pd.DataFrame(st.session_state.news_items).to_csv(csv_buffer, index=False)
    col3, col4 = st.columns([1, 1], gap="small")
    with col3:
        st.download_button("Download JSON", data=json_data, file_name="news.json", mime="application/json")
    with col4:
        st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="news.csv", mime="text/csv")
    
else:
    st.warning("Please enter an API key and a search query to start scraping.")
