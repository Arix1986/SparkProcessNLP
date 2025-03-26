import streamlit as st
import requests
import pandas as pd
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment variable
BACKEND_URL = os.getenv('BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("BACKEND_URL environment variable is not set")

def main():
    st.title("Aplicación de Búsqueda de Tweets")
    
    st.subheader("Ingrese los parámetros de búsqueda")
    search_terms = st.text_input("Términos de búsqueda (separados por comas)", "nvidia, AI")
    start_date = st.date_input("Fecha de inicio", date.today())
    end_date = st.date_input("Fecha de fin", date.today())
    max_items = st.number_input("Máximo de items", min_value=1, max_value=500, value=500)
    
    if st.button("Buscar"):
        # Convertir cadena a lista
        terms = [term.strip() for term in search_terms.split(",")]
        payload = {
            "search_terms": terms,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "max_items": max_items,
        }
        response = requests.post(BACKEND_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            st.success(data["message"])
            if data["results"]:
                df = pd.DataFrame(data["results"])
                st.dataframe(df)
            else:
                st.info("No se retornaron resultados.")
        else:
            st.error("Error: " + response.text)

if __name__ == "__main__":
    main()
