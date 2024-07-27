import streamlit as st
import pandas as pd
from pytube import YouTube
from streamlit_gsheets import GSheetsConnection

# Configuration of the page
st.set_page_config(page_title="You 2 be", page_icon="▶️")

# Establish connection with Google Sheets
# (Assuming you have set up the necessary authentication)
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data (replace "youtube_videos" with your actual sheet name)
df = conn.read(worksheet="youtube_videos", usecols=list(range(22)), ttl=5)
df = df.dropna(how="all")  # Remove rows with all NaN values

# Function to center text (optional)
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>", unsafe_allow_html=True)

def   
 main():
    # Sidebar for adding and selecting videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)

        # Show categories available (modify based on your sheet)
        centrar_texto("Videos", 4, 'white')
        df_categories = df["Category"].unique()
        df_categories = sorted(df_categories)
        selected_category = st.selectbox('Selecciona una categoría para ver los videos:', df_categories)

        # Filter data by category
        df = df[df["Category"] == selected_category]

        # Feature 2 filters (modify as needed)
        df_titles = df["Title"].unique()
        df_titles = sorted(df_titles)
        selected_title = st.selectbox('Titulo', df_titles)

        # Filter data by title
        df_video = df[df["Title"] == selected_title].iloc[0]

    # Main video player
    if 'selected_video_url' not in st.session_state:
        st.session_state.selected_video_url = df_video['URL']
    st.video(st.session_state.selected_video_url, autoplay=True)

    # Delete video functionality (assuming you have a column for deletion flag)
    if 'selected_video_idx' in st.session_state:
        selected_idx = st.session_state.selected_video_idx
        if st.button(f"Eliminar Video", key=f"delete_{selected_idx}"):
            # Update data in Google Sheets to mark video for deletion (modify logic as needed)
            df.loc[selected_idx, 'Delete'] = True  # Assuming a 'Delete' column exists
            conn.update(worksheet="youtube_videos", data=df)
            st.success("Video eliminado")
            del st.session_state['selected_video_url']
            del st.session_state['selected_video_idx']
            st.experimental_rerun()

    # Sidebar for adding videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        centrar_texto("Agregar video", 4, "white")

        # Input for video URL and category
        video_url = st.text_input("Ingresa la URL del video de YouTube:")
        # Input de texto para ingresar la categoría
        category = st.text_input("Ingresa la categoría del video:")

        # Botón para agregar el video
        if st.button("Agregar Video"):
            if video_url and category:
                video_id = extract_video_id(video_url)
                if video_id:
                    video_title = get_video_title(video_url)
                    if video_title:
                        add_video(category, video_url, video_title)
                        st.success(f"Video '{video_title}' agregado a la categoría '{category}'")
                        st.experimental_rerun()
                    else:
                        st.error("No se pudo obtener el título del video. Verifica la URL.")
                else:
                    st.error("Por favor, ingresa una URL de YouTube válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

    # Reproducción continua
    if st.session_state.continuous_playback and 'selected_video_idx' in st.session_state:
        filtered_df = df[df["Category"] == slb_1]
        current_index = st.session_state.selected_video_idx
        next_index = (current_index + 1) % len(filtered_df)
        next_video_url = filtered_df.iloc[next_index]['URL']

        # Reproducir el siguiente video automáticamente
        st.session_state.selected_video_url = next_video_url
        st.session_state.selected_video_idx = next_index
        st.experimental_rerun()

def extract_video_id(url):
    """
    Extrae el ID del video de una URL de YouTube.
    """
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

def get_video_title(url):
    """
    Obtiene el título de un video de YouTube usando pytube.
    """
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

def add_video(category, url, title):
    df = load_videos()
    new_row = pd.DataFrame({'Category': [category], 'URL': [url], 'Title': [title]})
    df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="youtube_videos", data=df)
    st.success("Video agregado con éxito")

def delete_video(index):
    df = load_videos()
    df = df.drop(index)
    conn.update(worksheet="youtube_videos", data=df)

if __name__ == "__main__":
    main()
