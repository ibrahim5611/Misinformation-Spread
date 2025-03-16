import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Set API Keys
GOOGLE_API_KEY = "AIzaSyCVGG8uPZB4FRf0gIY7Hs2nFe_4k9RRgMY"
NEWS_API_KEY = "385ccdae73384cc98e7fa71e40a257ae"

# Function to check misinformation
def google_fact_check(query):
    """Check misinformation using Google's Fact Check API"""
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={GOOGLE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if "claims" in data and data["claims"]:
        fact_checks = data["claims"]
        result_text = ""
        total_score = 0
        
        for claim in fact_checks[:3]:  
            rating = claim["claimReview"][0].get("textualRating", "No Rating").lower()
            source = claim["claimReview"][0].get("publisher", {}).get("name", "Unknown")
            url = claim["claimReview"][0].get("url", "#")
            
            if "true" in rating or "correct" in rating:
                risk_score = 10  
            elif "false" in rating or "incorrect" in rating:
                risk_score = 70  
            else:
                risk_score = 50  

            total_score += risk_score
            
            result_text += f"🔹 **Claim:** {claim.get('text', 'N/A')}\n"
            result_text += f"🔹 **Rating:** {rating.capitalize()}\n"
            result_text += f"🔹 **Source:** [{source}]({url})\n"
            result_text += f"🔹 **Assigned Risk Score:** {risk_score}/100\n\n"

        final_risk_score = total_score // len(fact_checks)
        
        return result_text, final_risk_score
    
    return "No fact-checking information available.", 90

# Function to fetch trending news from NewsAPI
def fetch_trending_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "articles" in data:
        articles = data["articles"]
        headlines = [article["title"] for article in articles if article["title"]]
        sources = [article["source"]["name"] for article in articles]
        return headlines[:10], sources[:10]  
    return [], []

# Function to fetch fake news sources by country
def fetch_fake_news_by_country():
    url = f"https://newsapi.org/v2/everything?q=fake&sortBy=popularity&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    country_data = []
    if "articles" in data:
        for article in data["articles"]:
            source = article["source"]["name"]
            country = article.get("country", "Unknown")  # Some sources may not have country info
            country_data.append({"source": source, "country": country})
    
    return country_data

# Function to create a heatmap
def create_misinformation_heatmap():
    st.sidebar.title("🌍 Fake News Heatmap")
    st.sidebar.write("Showing fake news trends by region.")
    
    # Fetch fake news sources by country
    country_data = fetch_fake_news_by_country()
    
    if not country_data:
        st.sidebar.warning("⚠️ Unable to fetch fake news locations. Check API key.")
        return
    
    # Convert data into a DataFrame
    df = pd.DataFrame(country_data)
    
    # Assign latitude and longitude (Hardcoded for simplicity)
    country_coords = {
        "USA": [37.0902, -95.7129], "UK": [55.3781, -3.4360], "India": [20.5937, 78.9629], 
        "Australia": [-25.2744, 133.7751], "Canada": [56.1304, -106.3468]
    }
    
    df["coords"] = df["country"].map(country_coords)  # Map country names to lat/lon
    
    # Filter out unknown locations
    df = df.dropna(subset=["coords"])
    
    # Create a Folium heatmap
    heatmap_map = folium.Map(location=[20, 0], zoom_start=2)
    HeatMap(df["coords"].tolist()).add_to(heatmap_map)
    
    st.sidebar.subheader("🌎 Global Misinformation Heatmap")
    folium_static(heatmap_map)

# Streamlit UI
st.title("📰 Misinformation Detector & Trend Tracker")
st.write("Enter a news headline or statement to verify if it's real or misinformation.")

# User Input
user_input = st.text_area("Enter News/Statement:")
if st.button("Check"):
    if user_input:
        result, risk_score = google_fact_check(user_input)
        st.subheader("Fact-Check Results:")
        st.markdown(result)
        
        st.subheader(f"🛑 Misinformation Risk Score: {risk_score}/100")
        if risk_score <= 30:
            st.success("✅ Low Risk: Likely to be true.")
        elif risk_score <= 70:
            st.warning("⚠️ Medium Risk: Could be misleading.")
        else:
            st.error("🚨 High Risk: Likely misinformation!")

    else:
        st.warning("Please enter some text.")

# Trending Fake News Tracker
st.sidebar.title("📊 Fake News Trend Tracker")
st.sidebar.write("Fetching trending news topics...")

# Fetch and display trending news
trending_news, trending_sources = fetch_trending_news()
if trending_news:
    st.sidebar.subheader("🔥 Top Trending News Headlines")
    df = pd.DataFrame({"Trending News": trending_news, "Source": trending_sources})
    
    # Plot trending news
    fig = px.bar(df, y="Trending News", orientation="h", title="Most Mentioned News Topics", color_discrete_sequence=["red"])
    st.sidebar.plotly_chart(fig, use_container_width=True)

else:
    st.sidebar.write("⚠️ Unable to fetch trending news. Check API key.")

# Display the misinformation heatmap
create_misinformation_heatmap()

st.sidebar.header("About")
st.sidebar.write("🚀 This app verifies misinformation using Google's Fact Check API and tracks fake news trends.")
