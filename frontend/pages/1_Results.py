import streamlit as st
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from api_requests import run_search_tweets
from wordcloud import WordCloud
import re
from collections import Counter
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Resultados del Análisis", layout="wide")

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
        with st.spinner("Obteniendo datos y analizando sentimientos..."):
            try:
                resultado = run_search_tweets(**st.session_state.data)
                st.session_state.result = resultado
                st.session_state.json_str = json.dumps(resultado, indent=4)
            except Exception as e:
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

    # # Gráfico de torta
    # st.subheader("📊 Distribución de Sentimientos")
    # fig, ax = plt.subplots()
    # sns.set_palette("pastel")
    # ax.pie(
    #     [len(positivos), len(negativos)],
    #     labels=["Positivos", "Negativos"],
    #     autopct='%1.1f%%',
    #     startangle=90,
    #     wedgeprops={"edgecolor": "white", "linewidth": 1},
    # )
    # ax.axis('equal')
    # st.pyplot(fig)

    # Distribución de Sentimientos y Confianza (Gráfico Polar)
    # Preparamos columnas auxiliares
    df['Clase'] = df['predict'].map({0: 'Negativo', 1: 'Positivo'})
    df['ClaseEmoji'] = df['Clase'].map({'Positivo': '😄 Positivo', 'Negativo': '😡 Negativo'})

    # Creamos ángulos tipo radar para darle forma circular
    np.random.seed(42)

    def asignar_theta(row):
        # Asignamos un ángulo distinto para cada clase
        return np.random.uniform(0, 90) if row['Clase'] == 'Positivo' else np.random.uniform(180, 270)

    df['theta'] = df.apply(asignar_theta, axis=1)

    # Gráfico polar
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
            angularaxis=dict(showticklabels=False)  # opcional
        ),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Histograma de confianza
    st.subheader("📈 Confianza del Modelo por Sentimiento")
    fig, ax = plt.subplots()
    sns.histplot(data=df, x='prob_float', hue='predict', bins=10, kde=True, ax=ax)
    ax.set_xlabel("Probabilidad (%)")
    ax.set_ylabel("Cantidad")
    ax.set_title("Distribución de Confianza")
    st.pyplot(fig)

    # Interpretación automática
    promedio_positivo = positivos['prob_float'].mean()
    promedio_negativo = negativos['prob_float'].mean()

    st.markdown("### 🧠 Interpretación del Modelo")
    st.write(f"""
    El modelo presenta una **confianza promedio de `{promedio_positivo:.2f}%` en tweets positivos** 
    y una **confianza promedio de `{promedio_negativo:.2f}%` en tweets negativos**.

    {"✅ El modelo se muestra más seguro clasificando tweets positivos." if promedio_positivo > promedio_negativo else "⚠️ El modelo se muestra más seguro clasificando tweets negativos."}

    Si muchas predicciones se acercan al 50%, esto puede indicar que el modelo tiene baja certeza y podría necesitar mejoras o ajustes en los datos de entrenamiento.
    """)

    # Nube de palabras
    st.subheader("☁️ Palabras Más Frecuentes")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Tweets Positivos")
        texto_positivo = " ".join(positivos['text'])
        nube_positiva = WordCloud(width=600, height=300, background_color='white').generate(texto_positivo)
        st.image(nube_positiva.to_array())
    with col2:
        st.write("Tweets Negativos")
        texto_negativo = " ".join(negativos['text'])
        nube_negativa = WordCloud(width=600, height=300, background_color='white').generate(texto_negativo)
        st.image(nube_negativa.to_array())

    # Tweets con mayor confianza
    st.subheader("🏆 Tweets con Mayor Confianza")
    st.markdown("#### Positivos")
    st.dataframe(positivos.sort_values(by='prob_float', ascending=False).head(5)[['text', 'prob']], use_container_width=True)

    st.markdown("#### Negativos")
    st.dataframe(negativos.sort_values(by='prob_float', ascending=False).head(5)[['text', 'prob']], use_container_width=True)

    # Ejemplos completos
    st.subheader("📄 Ejemplos de Tweets")
    with st.expander("Ver todos los Tweets Positivos"):
        st.dataframe(positivos[['text', 'prob']], use_container_width=True)
    with st.expander("Ver todos los Tweets Negativos"):
        st.dataframe(negativos[['text', 'prob']], use_container_width=True)

    # Descargar JSON
    st.subheader("⬇️ Descargar Resultados")
    st.download_button(
        label="Descargar JSON",
        data=st.session_state.json_str,
        file_name="resultados_analisis_sentimientos.json",
        mime="application/json",
    )
