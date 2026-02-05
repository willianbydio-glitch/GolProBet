import streamlit as st
import pandas as pd
import requests

# Configurações iniciais
st.set_page_config(page_title="GolBetPro Mobile", layout="centered")

st.title("⚽ GolBetPro v2.0")
st.write("Análise de Jogos em Tempo Real")

# --- BARRA LATERAL (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("API Key (Football-API)", type="password")
    
# --- ENTRADA DE DADOS ---
tab1, tab2 = st.tabs(["Análise Manual", "Dados da API"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        casa = st.text_input("Time Casa")
        gols_c = st.number_input("Gols Casa", min_value=0)
    with col2:
        fora = st.text_input("Time Fora")
        gols_f = st.number_input("Gols Fora", min_value=0)

    if st.button("Analisar Agora"):
        total = gols_c + gols_f
        btts = "Sim" if gols_c > 0 and gols_f > 0 else "Não"
        
        st.metric("Total de Gols", total)
        st.info(f"Ambas Marcam: {btts} | {'Over 2.5' if total > 2.5 else 'Under 2.5'}")

with tab2:
    st.write("Conecte sua API para buscar jogos do dia automaticamente.")
    if st.button("Buscar Jogos"):
        st.warning("Insira sua API Key na lateral para buscar dados reais.")
