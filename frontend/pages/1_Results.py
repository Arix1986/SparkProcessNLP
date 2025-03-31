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

# st.markdown("""
#     <style>
#     /* Oculta el menú y el pie de página de Streamlit */
#     #MainMenu, footer {visibility: hidden;}

#     /* Ajustes generales del layout */
#     .block-container {
#         padding-top: 2rem;
#         padding-bottom: 2rem;
#         padding-left: 2rem;
#         padding-right: 2rem;
#     }

#     /* Texto más claro y limpio */
#     html, body, [class*="css"]  {
#         font-family: 'Segoe UI', sans-serif;
#         color: #111;
#         background-color: #fff;
#     }

#     /* Estilo para títulos */
#     h1, h2, h3 {
#         color: #0D47A1;
#     }

#     /* Bordes suaves en dataframes y expander */
#     .stDataFrame, .stExpander {
#         border-radius: 10px;
#         border: 1px solid #ddd;
#         box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
#     }

#     /* Botones */
#     .stButton>button {
#         border-radius: 8px;
#         padding: 0.5rem 1rem;
#         background-color: #0D47A1;
#         color: white;
#         border: none;
#     }
#     .stButton>button:hover {
#         background-color: #1565C0;
#     }
#     </style>
# """, unsafe_allow_html=True)


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

                st.write("📤 Paso 2: Analizando tweets...")
                predicciones = asyncio.run(upload_file_and_predict(path_csv))

                st.write("🧠 Paso 3: Procesando resultados...")
                for i, item in enumerate(predicciones):
                    df.loc[i, 'predict'] = item['predict']
                    df.loc[i, 'prob'] = item['prob']

                st.session_state.result = df.to_dict('records')
                st.session_state.json_str = json.dumps(st.session_state.result, indent=4)
# Borrado
                # print("path_csv", path_csv)
                # if os.path.exists(path_csv): 
                #     os.remove(path_csv)

                # frontend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # csv_original_path = os.path.join(frontend_dir, "output", "scraped_tweets.csv")
                # print("csv_original_path", csv_original_path)
                # if os.path.exists(csv_original_path): 
                #     os.remove(csv_original_path)
# Hasta acá
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
    col_left, col_right = st.columns([2, 1]) 

    # Indicadores
    total_tweets = len(df)
    positive_pct = len(positivos) / total_tweets * 100 if total_tweets > 0 else 0
    negative_pct = len(negativos) / total_tweets * 100 if total_tweets > 0 else 0

    # Sentiment analysis message
    sentiment_message = ""
    celebration = False
    snow = False
    
    if positive_pct > 70:
        sentiment_message = "🎉 ¡Resultados excelentes! La mayoría de los comentarios son muy positivos. 🎉"
        celebration = True
        snow = True
    elif positive_pct > 55:
        sentiment_message = "👍 ¡Buenos resultados! Los comentarios son mayormente positivos."
        celebration = True
    elif negative_pct > 55:
        sentiment_message = "👎 Mayoría de comentarios negativos. Hay aspectos a mejorar."
    elif negative_pct > 70:
        sentiment_message = "⚠️ ¡Atención! La gran mayoría de comentarios son negativos. Se recomienda acción inmediata."
        celebration = False
    else:
        sentiment_message = "➖ Los comentarios son mayormente neutrales, con una mezcla de opiniones."
    
    st.markdown(f"### 📌 Análisis de Sentimiento: {sentiment_message}")
    
    # Optional celebration effect

    if celebration:
        st.balloons()
        st.success("¡Estos son resultados para celebrar!")
    
    if snow:
        st.snow()
    
    with col_left:
        # Gráfico polar
        df['Clase'] = df['predict'].map({0: 'Negativo', 1: 'Positivo'})
        df['ClaseEmoji'] = df['Clase'].map({'Positivo': '😄', 'Negativo': '😡'})

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
            color_discrete_map={'😄': 'green', '😡': 'red'},
            title="🌐 Visualización Polar de Confianza en las Predicciones",
            height=600
        )
        fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 100], showticklabels=True, tickfont=dict(color="black")),
                angularaxis=dict(showticklabels=False)
            ),
            showlegend=True,
            legend=dict(
                font=dict(size=24),  # Increased from 16 to 24 (approximately 2.5x default size)
                orientation="v",
                yanchor="top",
                y=0.5,
                xanchor="left",
                x=1.1,
                itemsizing='constant',  # Makes legend items more consistent in size
                title_text = 'Sentimiento',
                title_font_size=26
            ),
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # KPIs
        st.subheader("📊 Métricas Clave")
        
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <h3 style="margin: 0; color: white;">Total de Tweets</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 5px 0 0 0; color: white;">{len(df)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        positive_pct = len(positivos) / total_tweets * 100 if total_tweets > 0 else 0
        negative_pct = len(negativos) / total_tweets * 100 if total_tweets > 0 else 0
        
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: white;">Tweets Positivos</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 5px 0 0 0; color: white;">
                {len(positivos)} <span style="font-size: 20px; color: #4CAF50;">({positive_pct:.1f}%)</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: white;">Tweets Negativos</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 5px 0 0 0; color: white;">
                {len(negativos)} <span style="font-size: 20px; color: #F44336;">({negative_pct:.1f}%)</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # # Sentiment analysis message
        # st.markdown("### 📌 Análisis de Sentimiento")
        # st.markdown(f"<div style='color: white;'>{sentiment_message}</div>", unsafe_allow_html=True)
        
        if celebration:
            st.balloons()
            st.success("¡Estos son resultados para celebrar!")
        if snow:
            st.snow()

    # Top tweets
    st.subheader("🏆 Tweets con Mayor Confianza")
    st.markdown("#### Positivos")
    st.dataframe(positivos.sort_values(by='prob_float', ascending=False).head(5)[['text', 'prob']], use_container_width=True, 
                 column_config={
                "text": "Tweet",
                "prob": "Confianza"
            })

    st.markdown("#### Negativos")
    st.dataframe(negativos.sort_values(by='prob_float', ascending=False).head(5)[['text', 'prob']], use_container_width=True, 
                 column_config={
                "text": "Tweet",
                "prob": "Confianza"
            })

    # Tweets completos
    st.subheader("📄 Tweets")
    with st.expander("Ver todos los Tweets Positivos"):
        st.dataframe(positivos[['text', 'prob']], use_container_width=True,        
                     column_config={
                "text": "Tweet",
                "prob": "Confianza"
            })
    with st.expander("Ver todos los Tweets Negativos"):
        st.dataframe(negativos[['text', 'prob']], use_container_width=True,
                     column_config={
                "text": "Tweet",
                "prob": "Confianza"
            }
                     )

    # Descargar resultados
    st.subheader("⬇️ Descargar Resultados")
    st.download_button(
        label="Descargar JSON",
        data=st.session_state.json_str,
        file_name="resultados_analisis_sentimientos.json",
        mime="application/json",
    )
