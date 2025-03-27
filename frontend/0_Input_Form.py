import streamlit as st
from datetime import date

st.set_page_config(page_title="Análisis de Sentimientos", layout="wide")

# 💅 Estilo visual personalizado
st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        color: #111;
        background-color: #fff;
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
    </style>
""", unsafe_allow_html=True)

# 🧠 Título y descripción
st.title("🔍 Analiza la percepción pública sobre tu marca en Twitter")

st.markdown("""
Este módulo te permite obtener y analizar tweets relacionados con un tema, marca o palabra clave específica.

La herramienta está pensada para ayudarte a **entender cómo se sienten las personas respecto a tu marca o producto** en redes sociales, y cómo ese sentimiento puede impactar en tu estrategia de comunicación.
""")

# 📌 Entrada de parámetros
with st.container():
    st.header("📝 Parámetros de búsqueda")
    palabra_clave = st.text_input("📌 Palabra clave o hashtag (ej: #Python, OpenAI)", value="nvidia")
    fecha_inicio = st.date_input("📅 Fecha de inicio", value=date(2024, 3, 1))
    fecha_fin = st.date_input("📅 Fecha de fin", value=date(2024, 3, 10))

# ⚙️ Opciones avanzadas
with st.expander("⚙️ Opciones avanzadas de filtrado"):
    max_items = st.number_input("🔢 Número máximo de tweets a analizar", min_value=1, max_value=100, value=10)
    idioma = st.text_input("🌐 Idioma de los tweets (ej: 'es' para Español, 'en' para Inglés)", value="en")
    menciones = st.text_input("👥 Usuarios mencionados (separados por coma)", value="")
    min_favs = st.number_input("❤️ Mínimo de 'Me gusta'", min_value=0, value=5)
    min_respuestas = st.number_input("💬 Mínimo de respuestas", min_value=0, value=5)
    min_retweets = st.number_input("🔁 Mínimo de retweets", min_value=0, value=5)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        solo_video = st.checkbox("🎥 Solo tweets con video", value=False)
        solo_imagen = st.checkbox("🖼️ Solo tweets con imagen", value=False)
    with col2:
        solo_citas = st.checkbox("💬 Solo tweets citados", value=False)
        solo_verificados = st.checkbox("✅ Solo usuarios verificados", value=False)
    with col3:
        solo_twitter_blue = st.checkbox("💎 Solo usuarios con Twitter Blue", value=False)
        guardar_respuesta_completa = st.checkbox("💾 Guardar datos completos", value=True)

# 🚀 Botón de acción
st.markdown("###")
if st.button("🚀 Analizar Tweets"):
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
