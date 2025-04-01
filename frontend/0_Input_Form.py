import streamlit as st
from datetime import date
from PIL import Image
import os

st.set_page_config(page_title="Análisis de Sentimientos", layout="wide", initial_sidebar_state="collapsed")

# Asegurarse de que no hay estado anterior
if 'data' in st.session_state:
    del st.session_state['data']

# 💅 Estilo personalizado
st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}

    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background-color: #ffffff;
        color: #111;
    }

    h1, h2, h3 {
        color: #0D47A1;
    }

    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        background-color: #0D47A1;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
            
    /* Ocultar botón de Deploy */
    button[title="Deploy this app"] {
     display: none;
    }
    </style>
""", unsafe_allow_html=True)

# 🧠 Título y descripción
st.title("🔍 Analiza la percepción pública sobre tu marca en Twitter")

# 📐 Diseño en columnas
col_filtros, col_info = st.columns([1, 1])

max_tweets = 999

# 🔎 Columna izquierda: Filtros de búsqueda
with col_filtros:
    st.header("📝 Parámetros de búsqueda")
    palabra_clave = st.text_input("📌 Palabra clave o hashtag (ej: #Python, OpenAI)", value="nvidia")
    fecha_inicio = st.date_input("📅 Fecha de inicio", value=date(2024, 3, 1))
    fecha_fin = st.date_input("📅 Fecha de fin", value=date(2024, 3, 10))

    with st.expander("⚙️ Opciones avanzadas de filtrado"):
        max_items = st.number_input("🔢 Número máximo de tweets a analizar", min_value=1, value=10)
        if max_items > max_tweets:
            st.error("⚠️ El número máximo de tweets no puede ser mayor a "+str(max_tweets))
            
        idioma = st.text_input("🌐 Idioma (ej: 'es' para Español, 'en' para Inglés)", value="en")
        menciones = st.text_input("👥 Menciones (usuarios separados por coma)", value="")
        min_favs = st.number_input("❤️ Mínimo de 'Me gusta'", min_value=0, value=5)
        min_respuestas = st.number_input("💬 Mínimo de respuestas", min_value=0, value=5)
        min_retweets = st.number_input("🔁 Mínimo de retweets", min_value=0, value=5)

        col1, col2, col3 = st.columns(3)
        with col1:
            solo_video = st.checkbox("🎥 Solo con video", value=False)
            solo_imagen = st.checkbox("🖼️ Solo con imagen", value=False)
        with col2:
            solo_citas = st.checkbox("💬 Solo tweets citados", value=False)
            solo_verificados = st.checkbox("✅ Solo verificados", value=False)
        with col3:
            solo_twitter_blue = st.checkbox("💎 Solo Twitter Blue", value=False)
            guardar_respuesta_completa = st.checkbox("💾 Guardar datos completos", value=True)

    st.markdown("###")
    submit_button = st.button("🚀 Analizar Tweets")
    
    if submit_button:
        if max_items > max_tweets:
            st.error("❌ Por favor, reduce el número de tweets a analizar a un máximo de "+str(max_tweets))
        else:
            st.session_state.data = {
                "search_terms": palabra_clave.split(","),
                "start_date": fecha_inicio.strftime('%Y-%m-%d'),
                "end_date": fecha_fin.strftime('%Y-%m-%d'),
                "max_items": max_items,
                "tweet_language": idioma,
                "mentioning": menciones,
                "min_favorites": min_favs,
                "min_replies": min_respuestas,
                "min_retweets": min_retweets,
                "only_video": solo_video,
                "only_verified": solo_verificados,
                "only_image": solo_imagen,
                "only_quote": solo_citas,
                "only_twitter_blue": solo_twitter_blue,
                "keep_all_response_data": guardar_respuesta_completa,
            }
            st.switch_page("pages/1_Results.py")

# 🖼️ Columna derecha: Instrucciones + Imagen
with col_info:
    with st.expander("ℹ️ ¿Cómo funciona este módulo?", expanded=False):
        st.markdown("""
        Esta herramienta está diseñada para ayudarte a **descubrir qué piensan y sienten los usuarios de Twitter** sobre un tema, marca o producto en particular.

        ### ✅ Pasos para utilizarlo:
        1. Ingresa una **palabra clave o hashtag** de interés.
        2. Define el **rango de fechas**.
        3. Opcionalmente, ajusta los filtros avanzados.
        4. Haz clic en **"Analizar Tweets"**.

        El sistema recopilará los tweets, los enviará a un modelo de análisis de sentimientos y te devolverá una visualización interactiva con los resultados.

        Ideal para:  
        - Departamentos de marketing.  
        - Análisis de reputación.  
        - Seguimiento de campañas y eventos.  
        """)
    
    # Imagen siempre visible debajo del expander
    image_path = os.path.join(os.path.dirname(__file__), "static", "sentiment_cover_v1.png")
    st.image(image_path, use_container_width=True)

