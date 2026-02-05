import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GolBetPro AI", page_icon="⚽")

# --- FUNÇÃO DA IA (PREDIÇÃO) ---
def realizar_predicao(gols_c, gols_f):
    # Criando um dataset de treino rápido (Vitória Casa=1, Empate=0, Vitória Fora=2)
    # Aqui a IA aprende que muitos gols em casa = vitória casa, etc.
    data = {
        'gols_casa': [3, 0, 1, 5, 1, 0, 2, 4],
        'gols_fora': [0, 3, 1, 1, 2, 0, 2, 0],
        'resultado': [1, 2, 0, 1, 2, 0, 0, 1]
    }
    df = pd.DataFrame(data)
    
    modelo = RandomForestClassifier(n_estimators=100)
    modelo.fit(df[['gols_casa', 'gols_fora']], df['resultado'])
    
    pred = modelo.predict([[gols_c, gols_f]])
    prob = modelo.predict_proba([[gols_c, gols_f]])
    return pred[0], max(prob[0]) * 100

# --- INTERFACE ---
st.title("⚽ GolBetPro Inteligência Artificial")

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Sua API Key", type="password")
    liga = st.selectbox("Escolha a Liga", ["Premier League", "Brasileirão", "La Liga"])
    liga_id = {"Premier League": 39, "Brasileirão": 71, "La Liga": 140}[liga]

# --- LÓGICA DE BUSCA ---
if st.button("🔄 Buscar e Analisar Jogos de Hoje"):
    if not api_key:
        st.error("Por favor, insira sua API Key na barra lateral!")
    else:
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {'x-apisports-key': api_key}
        params = {"league": liga_id, "season": 2024, "next": 10} # Busca próximos 10 jogos
        
        try:
            response = requests.get(url, headers=headers, params=params)
            jogos = response.json()['response']
            
            if not jogos:
                st.warning("Nenhum jogo encontrado para esta liga hoje.")
            
            for jogo in jogos:
                casa = jogo['teams']['home']['name']
                fora = jogo['teams']['away']['name']
                
                # Usamos a média de gols da temporada para a IA (exemplo simplificado)
                res, confianca = realizar_predicao(2, 1) # Simulação de input para IA
                
                with st.expander(f"{casa} vs {fora}"):
                    col1, col2 = st.columns(2)
                    col1.metric("Palpite IA", "Casa" if res==1 else "Fora" if res==2 else "Empate")
                    col2.metric("Confiança", f"{confianca:.1f}%")
                    st.write(f"Data: {jogo['fixture']['date']}")
                    
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")

# --- ENTRADA MANUAL ---
st.divider()
st.subheader("🧪 Teste a IA Manualmente")
c1, c2 = st.columns(2)
gc = c1.number_input("Gols Médios Casa", 0.0, 5.0, 1.5)
gf = c2.number_input("Gols Médios Fora", 0.0, 5.0, 1.2)

if st.button("Calcular Probabilidade"):
    res, conf = realizar_predicao(gc, gf)
    st.success(f"Resultado provável: {res} com {conf}% de chance.")
