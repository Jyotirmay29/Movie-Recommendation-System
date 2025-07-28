import streamlit as st
import pandas as pd
import requests
import pickle
import time
import warnings
import random

# Optional: Suppress warnings in the terminal
warnings.filterwarnings("ignore")
# Load movie data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

# Get recommendations based on selected movie
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# Fetch poster with retry and fallback
def fetch_poster(movie_id, retries=3, delay=1):
    api_key = '6d028f4f69eb1b3c4c413a30ab59a92c'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')

            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}", False
            else:
                return "https://via.placeholder.com/130x200.png?text=No+Image", True

        except requests.exceptions.RequestException:
            time.sleep(delay * (2 ** attempt) + random.uniform(0, 0.5))

    return "https://via.placeholder.com/130x200.png?text=Error", True

# Streamlit UI
st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.subheader("Top 10 Recommended Movies:")

    for i in range(0, 10, 5):
        cols = st.columns(5)
        for col, j in zip(cols, range(i, i + 5)):
            if j < len(recommendations):
                movie_title = recommendations.iloc[j]['title']
                movie_id = recommendations.iloc[j]['movie_id']
                poster_url, is_missing = fetch_poster(movie_id)

                with col:
                    st.image(poster_url, width=130)
                    st.caption(movie_title)
                    if is_missing:
                        st.markdown("<span style='color:red; font-size:12px;'>Poster not available</span>", unsafe_allow_html=True)
