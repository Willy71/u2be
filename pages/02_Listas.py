# API_KEY = st.secrets["youtube"]["api_key"]
# channelId='UC6k75c31768jOTvq38SQf6w',

# Clave de la API de YouTube
#API_KEY = st.secrets["youtube"]["api_key"]
# Configuración de la página
#st.set_page_config(page_title="YouTube Playlist Player", page_icon="❤")
#channelId='UCpVi9NfcKzRmNyVFkbsq3lA'

import streamlit as st
from googleapiclient.discovery import build

# Configuración de la página
st.set_page_config(page_title="YouTube Playlist Player", page_icon="❤")

# Clave de la API de YouTube
api_key = st.secrets["youtube"]["api_key"]

# Crear el cliente de la API de YouTube
youtube = build('youtube', 'v3', developerKey=api_key)

# Función para centrar el texto
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

def get_playlists(channel_id):
    # Recuperar listas de reproducción del canal
    request = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=25
    )
    response = request.execute()
    return response['items']

def get_videos(playlist_id):
    # Recuperar videos dentro de una lista de reproducción
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    return response['items']

def main():
    #centrar_texto("❤ ❤ SamyTube Player ❤ ❤", 2, 'pink')
    #st.sidebar.title("Opciones")

    # Entradas de texto para la API key y el channel ID
    #api_key = st.sidebar.text_input("Ingresa tu API Key", type="password")
    channel_id = st.sidebar.text_input("Ingresa un Channel ID")
    #channel_id = "UCpVi9NfcKzRmNyVFkbsq3lA"

    if api_key and channel_id:
        youtube = build('youtube', 'v3', developerKey=api_key)
        try:
            playlists = get_playlists(channel_id)
            playlist_titles = [playlist['snippet']['title'] for playlist in playlists]
            selected_playlist = st.sidebar.selectbox("Selecciona una lista de reproducción", playlist_titles)

            if selected_playlist:
                playlist_id = next(playlist['id'] for playlist in playlists if playlist['snippet']['title'] == selected_playlist)
                videos = get_videos(playlist_id)
                video_ids = [video['snippet']['resourceId']['videoId'] for video in videos]

                # Mostrar miniaturas y títulos en la barra lateral
                st.sidebar.markdown("### Videos en la lista de reproducción")
                clicked_video_id = st.sidebar.radio(
                    "Selecciona un video para reproducir",
                    video_ids,
                    format_func=lambda vid_id: next(video['snippet']['title'] for video in videos if video['snippet']['resourceId']['videoId'] == vid_id)
                )

                # Generar la lista de reproducción en formato JavaScript
                playlist = ','.join(video_ids)

                # Insertar el reproductor de YouTube centrado
                st.markdown(f"""
                <div style="display: flex; justify-content: center;">
                    <iframe id="player" type="text/html" width="832" height="507"
                    src="https://www.youtube.com/embed/{clicked_video_id}?playlist={playlist}&autoplay=1&controls=1&loop=1"
                    frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Por favor, selecciona una lista de reproducción.")
        except Exception as e:
            st.error(f"Error al recuperar datos de YouTube: {e}")
    else:
        st.warning("Por favor, ingresa tu API Key y Channel ID.")
        
st.sidebar.text("Willy UC6k75c31768jOTvq38SQf6w")
st.sidebar.text("Samy UCpVi9NfcKzRmNyVFkbsq3lA")

if __name__ == "__main__":
    main()

