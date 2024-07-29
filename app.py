import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials
from pytube import YouTube

# Configuración de la página
st.set_page_config(
    page_title="You 2 be",
    page_icon="▶️",
)

#=============================================================================================================================
# Conexion via gspread a traves de https://console.cloud.google.com/ y Google sheets

# Credenciales de Google como un diccionario
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "estacionamentosantarita",
  "private_key_id": "be360b61325e9a7647fb666ba8022492a4fb10ab",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPLbzTqxWlCH9l\nc5iBrzg7/JRlozvBMSqX9C17rM1PQJUdsX5EJVg+2jaj0d/xBWN0SWDOm5izliLk\nC3dw3irpEke4VNeOuJvttGVRjxUOza8H1HbQdZYd2HyG9xmocOc21B/Br8xtS5HX\nbEh1aXfIKyvWGUPjdMOGMyJv2lc2axLDiY2TymHa713scB9O52z2bl+0QPzCxYmm\nHurfP9sP3DEfU8DBaV6VFxMKbZCIbJvDBaJKvxnya8FnrXuPUTfqYhk+Ae6mYhb5\nGnNK1VblJwIhdUlfVBwXaEvCHPdpCcxvZoVKPtIzUy38Wkp+RbVCpbaDE3cCUQ8c\nqAHnBkKFAgMBAAECggEAEkXgjMzFeAzDuI3iN07Eh3a6G5LMbB6eUp1JpUny9WWa\nIVUGPXo+8JNsVIIBne9ebvAjFsxeqTkTP7wKxb/N1uImK3BnbyICNfKxj88UybCQ\nTc3KYvPg3YxtqbVbcOG9MVB/sorpkJqkznRkmawUazYl9vHu7Ndfs9NVWyDNwDG3\nayIk/vRf/4m0n9Pox4v7a3whSSKgXqcXwtzDLOBNCkQJXqwoPHHrG+hLPm22+Dq2\nQOBX/H50ZUkmJ0qLLUHNk62M/+pFzO2NlRAJzxBY/IJwFB3S9Tb6cK5nS4c5YTPz\nVSa4kfbpLInK24a1Q5lx/BME5PEKHxZoSwE4ZRQWKwKBgQDopUtMN1m49c78iRXx\nIHglUCGABFT8yf46GQZNakSZ0n33gvDCnoWXyrbv2RYBNBHLC3gc0knZXicgyeTA\n7eglfqrq0zgfEHAYUOj+iGyxOYC00Blvmm1fN6bNpLC4s48jMVb+BoSpaIU4StNQ\nCG6aI/PDIgFQXhbzVvAamZQeEwKBgQDj+fkAFID4A/7MWPFpWkJ89N/ePrPcGD9B\nnHVv93gkksZXScG3XimyVAKlm5CoESlIsdb5qxGl8K2dm312Xmu253XeycZYyoEc\ntLnTXRngyduODBm89lfetk8Q28ularXPoamtb/V0kB+6whRP0kUHxPri22BKYGgt\nl+tQP47QBwKBgH2xUI1NGlyj8cDfD8vHDyKZuH/B12j8eS5Kdu08jPPOleA0DoAX\nxXXNQCk10H219CcPe0WXF+8ov1snuT/DSbl4Rj+4/olKCEYa8McUTiUyPCd0h0mU\n1aKsHqLcZ95ipOMOtUFppCMjJVbUlnaXF6qP4hN7O9p/+0Zdoju83hmhAoGBAIhG\n/VnW5+FaQg3VfToFAom/t7MauFlxBR8rb+gmfmMeegHjzTDX0QUQwyRMAgT1fUA/\nTsqgQER5ws7cC/ueJbWIVyV+aFrbcqK+RfbbSITfJaecBCa4+33ebRUeznVrfJNJ\niCxtKMUtAkqZiZrNjwY98dt6V+0eBCh9D+VAmRYxAoGAJG2a9nJYC6T3zdJR77PP\naFsynYME5lQB3EvXICWAix5OWiSU1UxtbhmN0FleZq7TGQSgLhY5oj4LImXl71Qy\nboeVrIXuMS8RxMf8tkMd7jk5kTJfVoX907LJxYzRRPjKLVbHHyIRym3g1iILZhxz\nf5s5cGDrP+lO/CGB6Tzt4Vs=\n-----END PRIVATE KEY-----\n",
  "client_email": "you2be-conection@estacionamentosantarita.iam.gserviceaccount.com",
  "client_id": "108032461240752891545",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/you2be-conection%40estacionamentosantarita.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales y autorizar
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
gc = gspread.authorize(credentials)

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = '1NQN92mhMxhhj9CP3OfYxo_aowkI74y49sSPvStIiXn0'  # Reemplaza con la clave de tu documento
SHEET_NAME = 'youtube_videos'  # Nombre de la hoja dentro del documento
#=============================================================================================================================

try:
    sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"No se encontró la hoja de cálculo con la clave '{SPREADSHEET_KEY}'. Asegúrate de que la clave es correcta y que has compartido la hoja con el correo electrónico del cliente de servicio.")
except gspread.exceptions.APIError as e:
    st.error(f"Error de API al intentar acceder a la hoja de cálculo: {e}")
except Exception as e:
    st.error(f"Ha ocurrido un error inesperado: {e}")
    
# Función para centrar el texto
def centrar_texto(texto, tamanho, color):
    st.markdown(f"<h{tamanho} style='text-align: center; color: {color}'>{texto}</h{tamanho}>",
                unsafe_allow_html=True)

# Cargar los videos desde Google Sheets
@st.cache_data
def load_videos():
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
    return df

# Agregar un video a Google Sheets
def add_video(category, url, title):
    new_row = {'Category': category, 'URL': url, 'Title': title}
    sheet.append_row(list(new_row.values()))

# Eliminar un video de Google Sheets
#def delete_video(index):
#    sheet.delete_row(index + 2)  
# # +2 porque Google Sheets es 1-indexed y hay una fila de encabezado

# Eliminar un video de Google Sheets
def delete_video(url):
    cell = sheet.find(url)
    if cell:
        sheet.delete_row(cell.row)


def main():
    # Sidebar para agregar y seleccionar videos
    with st.sidebar:
        # Mostrar categorías disponibles
        centrar_texto("Videos", 2, 'white')
        df = load_videos()
        
        # Feature 1 filters
        df_1 = df["Category"].unique()
        df_1_1 = sorted(df_1)
        slb_1 = st.selectbox('Categoria', df_1_1)
        # Filter out data
        df = df[(df["Category"] == slb_1)]
        
        # Feature 2 filters
        df_2 = df["Title"].unique()
        df_2_1 = sorted(df_2)
        slb_2 = st.selectbox('Titulo', df_2_1)
        # Filter out data
        df = df[(df["Title"] == slb_2)]
             
        df_video = df[df["Title"] == slb_2].iloc[0]

        # Reproductor principal de video
        if 'selected_video_url' not in st.session_state:
            st.session_state.selected_video_url = df_video['Url']

        st.session_state.selected_video_url = df_video['Url']

    # Reproductor principal de video
    if 'selected_video_url' in st.session_state:
        st.video(st.session_state.selected_video_url, autoplay=False)

        if st.session_state.selected_video_url:
            if st.button("Eliminar Video"):
                delete_video(st.session_state.selected_video_url)
                st.success("Video eliminado")
                del st.session_state['selected_video_url']
                st.rerun()
       
    # Sidebar para agregar videos
    with st.sidebar:
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#1717dc;" /> """, unsafe_allow_html=True)
        centrar_texto("Agregar video", 2, "white")

        # Input de texto para ingresar la URL del video de YouTube
        video_url = st.text_input("URL del video de YouTube:")

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
                        st.rerun()
                    else:
                        st.error("No se pudo obtener el título del video. Verifica la URL.")
                else:
                    st.error("Por favor, ingresa una URL de YouTube válida.")
            else:
                st.error("Por favor, ingresa una URL y una categoría.")

@st.cache_data
def extract_video_id(url):  
    # Extrae el ID del video de una URL de YouTube.
    regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(regex, url)
    if match:
        return match.group(6)
    return None

def get_video_title(url):
    # Obtiene el título de un video de YouTube usando pytube.
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        st.error(f"Error al obtener el título del video: {e}")
        return None

if __name__ == "__main__":
    main()
