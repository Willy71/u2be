# API_KEY = st.secrets["youtube"]["api_key"]
# channelId='UC6k75c31768jOTvq38SQf6w',

import streamlit as st
from googleapiclient.discovery import build

# Configuración de la página
st.set_page_config(page_title="YouTube Playlist Player", page_icon="▶️")

def get_playlists(youtube, channel_id):
    # Recuperar listas de reproducción del canal
    request = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=25
    )
    response = request.execute()
    return response['items']

def get_videos(youtube, playlist_id):
    # Recuperar videos dentro de una lista de reproducción
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    return response['items']

def main():
    st.title("YouTube Playlist Player")
    st.sidebar.title("Opciones")

    # Entradas de texto para la API key y el channel ID
    api_key = st.secrets["youtube"]["api_key"]
    st.text("UCpVi9NfcKzRmNyVFkbsq3lA")
    channel_id = st.sidebar.text_input("Ingresa un Channel ID")
    

    if api_key and channel_id:
        youtube = build('youtube', 'v3', developerKey=api_key)
        playlists = get_playlists(youtube, channel_id)
        playlist_titles = [playlist['snippet']['title'] for playlist in playlists]
        selected_playlist = st.sidebar.selectbox("Selecciona una lista de reproducción", playlist_titles)

        if selected_playlist:
            playlist_id = next(playlist['id'] for playlist in playlists if playlist['snippet']['title'] == selected_playlist)
            videos = get_videos(youtube, playlist_id)
            video_ids = [video['snippet']['resourceId']['videoId'] for video in videos]

            # Generar la lista de reproducción en formato JavaScript
            playlist = ','.join(video_ids)

            # Insertar el reproductor de YouTube con la lista de reproducción
            st.markdown(f"""
            <iframe id="player" type="text/html" width="640" height="390"
            src="https://www.youtube.com/embed/{video_ids[0]}?playlist={playlist}&autoplay=1&controls=1&loop=1"
            frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            """, unsafe_allow_html=True)
        else:
            st.warning("Por favor, selecciona una lista de reproducción.")
    else:
        st.warning("Por favor, ingresa tu API Key y Channel ID.")

if __name__ == "__main__":
    main()
