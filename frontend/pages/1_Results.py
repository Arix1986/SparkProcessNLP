import csv
import streamlit as st
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from api_requests import scrape_and_prepare_csv, upload_file_and_predict
from wordcloud import WordCloud
import re
from collections import Counter
import plotly.express as px
import numpy as np
import asyncio
import os

st.set_page_config(page_title="Resultados del Análisis", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Oculta el menú y el pie de página de Streamlit */
    #MainMenu, footer {visibility: hidden;}

    /* Ajustes generales del layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Texto más claro y limpio */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        color: #111;
        background-color: #fff;
    }

    /* Estilo para títulos */
    h1, h2, h3 {
        color: #0D47A1;
    }

    /* Bordes suaves en dataframes y expander */
    .stDataFrame, .stExpander {
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
    }

    /* Botones */
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


if 'data' not in st.session_state:
    st.error("No se encontraron datos de entrada. Por favor, vuelve a la página principal.")
    st.stop()

if 'skip_analysis' not in st.session_state:
    st.session_state.skip_analysis = False

if st.button("Volver al Formulario"):
    st.session_state.skip_analysis = True
    st.session_state.data = None
    st.session_state.result = None
    st.session_state.json_str = None
    st.switch_page("0_Input_Form.py")

if not st.session_state.skip_analysis:
    st.title("📊 Resultados del Análisis de Sentimientos")

    if 'result' not in st.session_state or st.session_state.result is None:
        with st.status("🕵️ Iniciando análisis de sentimientos...", expanded=True) as estado:
            try:
                st.write("🔍 Paso 1: Obteniendo tweets desde Twitter...")
                path_csv, df = asyncio.run(scrape_and_prepare_csv(st.session_state.data))

                st.write("📤 Paso 2: Enviando tweets al backend para limpieza y análisis...")
                predicciones = asyncio.run(upload_file_and_predict(path_csv))

                st.write("🧠 Paso 3: Procesando resultados...")
                for i, item in enumerate(predicciones):
                    df.loc[i, 'predict'] = item['predict']
                    df.loc[i, 'prob'] = item['prob']

                st.session_state.result = df.to_dict('records')
                st.session_state.json_str = json.dumps(st.session_state.result, indent=4)

                print("path_csv", path_csv)
                if os.path.exists(path_csv): 
                    os.remove(path_csv)

                frontend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                csv_original_path = os.path.join(frontend_dir, "output", "scraped_tweets.csv")
                print("csv_original_path", csv_original_path)
                if os.path.exists(csv_original_path): 
                    os.remove(csv_original_path)

                estado.update(label="✅ Análisis completado con éxito", state="complete")
            except Exception as e:
                estado.update(label="❌ Error durante el análisis", state="error")
                st.error(f"Ocurrió un error durante el análisis: {str(e)}")
                st.stop()

    resultado = st.session_state.result
    df = pd.DataFrame(resultado)
    df['prob_float'] = df['prob'].str.replace('%', '').astype(float)

    positivos = df[df['predict'] == 1]
    negativos = df[df['predict'] == 0]

    # KPIs
    st.header("🔢 Resumen Ejecutivo")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Tweets", len(df))
    col2.metric("Tweets Positivos", len(positivos))
    col3.metric("Tweets Negativos", len(negativos))

    # Gráfico polar
    df['Clase'] = df['predict'].map({0: 'Negativo', 1: 'Positivo'})
    df['ClaseEmoji'] = df['Clase'].map({'Positivo': '😄 Positivo', 'Negativo': '😡 Negativo'})

    np.random.seed(42)
    def asignar_theta(row):
        return np.random.uniform(0, 90) if row['Clase'] == 'Positivo' else np.random.uniform(180, 270)
    df['theta'] = df.apply(asignar_theta, axis=1)

    st.subheader("🧭 Distribución de Sentimientos y Confianza (Gráfico Polar)")
    fig = px.scatter_polar(
        df,
        r='prob_float',
        theta='theta',
        color='ClaseEmoji',
        symbol='Clase',
        size='prob_float',
        color_discrete_map={'😄 Positivo': 'green', '😡 Negativo': 'red'},
        title="🌐 Visualización Polar de Confianza en las Predicciones",
        height=600
    )
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=True, tickfont=dict(color="black")),
            angularaxis=dict(showticklabels=False)
        ),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top tweets
    st.subheader("🏆 Tweets con Mayor Confianza")
    st.markdown("#### Positivos")
    st.dataframe(positivos.sort_values(by='prob_float', ascending=False).head(5)[['text', 'prob']], use_container_width=True)

    st.markdown("#### Negativos")
    st.dataframe(negativos.sort_values(by='prob_float', ascending=False).head(5)[['text', 'prob']], use_container_width=True)

    # Tweets completos
    st.subheader("📄 Tweets")
    with st.expander("Ver todos los Tweets Positivos"):
        st.dataframe(positivos[['text', 'prob']], use_container_width=True)
    with st.expander("Ver todos los Tweets Negativos"):
        st.dataframe(negativos[['text', 'prob']], use_container_width=True)

    # Descargar resultados
    st.subheader("⬇️ Descargar Resultados")
    st.download_button(
        label="Descargar JSON",
        data=st.session_state.json_str,
        file_name="resultados_analisis_sentimientos.json",
        mime="application/json",
    )
