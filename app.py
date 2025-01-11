import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        spotify_url = track["external_urls"]["spotify"]
        return album_cover_url, spotify_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", "#"


def recommend(song):
    try:
        index = music[music['song'] == song].index[0]
    except IndexError:
        return [], [], [] 

    if index >= len(similarity):
        return [], [], []  
    
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_music_names = []
    recommended_music_posters = []
    recommended_spotify_links = []

    for i in distances[1:6]:  
        artist = music.iloc[i[0]].artist
        album_cover_url, spotify_url = get_song_album_cover_url(music.iloc[i[0]].song, artist)
        recommended_music_posters.append(album_cover_url)
        recommended_music_names.append(music.iloc[i[0]].song)
        recommended_spotify_links.append(spotify_url)

    return recommended_music_names, recommended_music_posters, recommended_spotify_links

st.set_page_config(page_title="Music Recommender", page_icon="🎶", layout="centered")

st.markdown("""
    <style>
        .header { text-align: center; font-size: 2rem; color: #4CAF50; }
        .song-title { font-size: 1.5rem; font-weight: bold; color: #2E8B57; }
        .recommendation-container { display: flex; flex-wrap: wrap; justify-content: start; gap: 20px; }
        .recommendation-item { text-align: center; margin: 20px; border: 2px solid #4CAF50; border-radius: 10px; padding: 10px; width: 150px; }
        .recommendation-item img { width: 100%; border-radius: 5px; }
        .search-container { text-align: center; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>Welcome to the Music Recommender System 🎶</div>", unsafe_allow_html=True)

search_query = st.text_input("Search for a song", placeholder="Enter song name...")

if search_query:
    filtered_music = music[music['song'].str.contains(search_query, case=False, na=False)]

    if not filtered_music.empty:
        selected_song = st.selectbox("Select a song from the results", filtered_music['song'].values)

        if st.button('Show Recommendations'):
            recommended_music_names, recommended_music_posters, recommended_spotify_links = recommend(selected_song)

            if recommended_music_names and recommended_music_posters:
                st.markdown(f"<div class='song-title'>Recommended songs for '{selected_song}'</div>", unsafe_allow_html=True)

                st.markdown("<div class='recommendation-container'>", unsafe_allow_html=True)
                for name, poster, spotify_url in zip(recommended_music_names, recommended_music_posters, recommended_spotify_links):
                    st.markdown(f"""
                        <div class='recommendation-item'>
                            <img src='{poster}' alt='Album Cover'>
                            <p>{name}</p>
                            <a href='{spotify_url}' target='_blank'>
                                <button style="padding: 8px 12px; background-color: #1DB954; color: white; border: none; border-radius: 5px; cursor: pointer;">Play on Spotify</button>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning(f"Sorry, no recommendations found for '{selected_song}'. Try another song!")
    else:
        st.warning("No songs found with that name. Please try again.")
else:
    st.markdown("<div class='search-container'>Please enter a song name to search for recommendations!</div>", unsafe_allow_html=True)
