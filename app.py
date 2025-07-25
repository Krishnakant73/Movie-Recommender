import streamlit as st
import pickle
import pandas as pd
import requests
from time import sleep


# API Configuration

API_KEY = "dc89002fde93cc002b5195c82c976b1"
BEARER_TOKEN = (
    "eyJhbGciOiJIUzI1NiJ9."
    "eyJhdWQiOiJkOWM4OTAwMmZkZTkzY2MwMDJiNTE5NWM4MmM5NzZiMSIsIm5iZiI6MTc1MzQ3MTc5OC4yNTIs"
    "InN1YiI6IjY4ODNkYjM2ZjU2Yjg5YzQ5YjUyYTZlMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9u"
    "IjoxfQ.ZJ6OOBfGhFPYdA2iHrSnB9F9Fm-cXx4ZAMAITQGjqfo"
)

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


# Function to fetch poster

@st.cache_data(ttl=3600)
def fetch_poster(movie_id):
    if not movie_id:
        return "https://via.placeholder.com/500x750?text=No+Poster"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=Error"


# Recommender function

def recommend(selected_title):
    try:
        idx = movies[movies["title"] == selected_title].index[0]
        distances = similarity[idx]
        recommendations = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]

        titles, posters = [], []
        for rec_idx, _ in recommendations:
            movie_id = movies.iloc[rec_idx].get("id")
            titles.append(movies.iloc[rec_idx]["title"])
            posters.append(fetch_poster(movie_id))
        return titles, posters

    except IndexError:
        st.error("❌ Movie not found!")
        return [], []


# Load Data

@st.cache_data
def load_data():
    try:
        with open("movie_dict.pkl", "rb") as f:
            movies_dict = pickle.load(f)
        with open("similarity.pkl", "rb") as f:
            sim = pickle.load(f)
        return pd.DataFrame(movies_dict), sim
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

movies, similarity = load_data()


# Streamlit Page Config

st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")


# Dark Mode Toggle

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode


# CSS Styles for Dark/Light

bg_dark = "background: linear-gradient(135deg, #00ADB5, #393E46);"
bg_light = "background: linear-gradient(135deg, #e0f7fa, #ffffff);"

st.markdown(
    f"""
    <style>
    .stApp {{ {bg_dark if dark_mode else bg_light} min-height:100vh; }}
    .title {{ text-align:center; font-size:48px; color:{'#EEEEEE' if dark_mode else '#00ADB5'}; }}
    .subtitle {{ text-align:center; font-size:20px; color:{'#EEEEEE' if dark_mode else '#393E46'}; margin-bottom:30px; }}
    .movie-card {{ border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1); cursor:pointer; background:{'#2C2F36' if dark_mode else '#FFF'}; }}
    .movie-title {{ text-align:center; font-size:16px; font-weight:600; color:{'#EEEEEE' if dark_mode else '#222831'}; margin:10px; }}
    .stButton>button {{ background-color:{'#393E46' if dark_mode else '#00ADB5'}; color:white; border-radius:8px; padding:0.5em 1.5em; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# App Layout

st.markdown('<div class="title">🎥 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ Discover movies you\'ll love ✨</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    choice = st.selectbox("👇 Pick a movie:", movies["title"].values)
    if st.button("🔍 Get Recommendations"):
        with st.spinner("Fetching recommendations..."):
            names, images = recommend(choice)
        if names:
            st.markdown("---")
            rec_cols = st.columns(5)
            for i, col in enumerate(rec_cols):
                if i < len(names):
                    col.markdown(
                        f"""
                        <div class="movie-card">
                            <img src="{images[i]}" width="100%" alt="{names[i]}">
                            <div class="movie-title">{names[i]}</div>
                        </div>
                        """,
                      unsafe_allow_html=True,
                    )

# Close main div
st.markdown("</div>", unsafe_allow_html=True)