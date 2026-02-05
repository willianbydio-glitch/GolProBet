import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GolBetPro AI", page_icon="⚽")

# --- FUNÇÃO DE CARREGAMENTO (AJUSTADA PARA O SEU CSV) ---
@st.cache_data
def carregar_dados_treinamento():
    try:
        # Carrega o seu arquivo brazi.csv
        df = pd.read_csv('brazil.csv') 
        
        # Mapeamento conforme seu arquivo: H (Casa) -> 1, D (Empate) -> 0, A (Fora) -> 2
        mapeamento = {'H': 1, 'D': 0, 'A': 2}
        
        dados_ia = pd.DataFrame()
        # Ajustado para os nomes das colunas do SEU arquivo (HG, AG, Res)
        dados_ia['media_gols_casa'] = df['HG']
        dados_ia['media_gols_fora'] = df['AG']
        dados_ia['resultado'] = df['Res'].map(mapeamento)
        
        return dados_ia.dropna()
    except Exception as e:
        st.error(f"Erro ao ler brazil.csv: {e}")
        return None

# --- IA DE PREDIÇÃO ---
def realizar_predicao_expert(gols_c, gols_f):
    dados = carregar_dados_treinamento()
    if dados is not None:
        X = dados[['media_gols_casa', 'media_gols_fora']]
        y = dados['resultado']
        modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        modelo.fit(X, y)
        return modelo.predict_proba([[gols_c, gols_f]])[0]
    return [0.33, 0.33, 0.34]

# --- INTERFACE ---
st.title("⚽ GolBetPro AI")

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Sua API Key", type="password")
    liga_nome = st.selectbox("Liga", ["Brasileirão", "Premier League"])
    liga_id = {"Brasileirão": 71, "Premier League": 39}[liga_nome]

# --- SIMULAÇÃO MANUAL ---
st.subheader("🧪 Simulação")
c1, c2 = st.columns(2)
gc = c1.number_input("Gols Casa", 0.0, 5.0, 1.5)
gf = c2.number_input("Gols Fora", 0.0, 5.0, 1.2)

if st.button("Analisar Simulação"):
    prob = realizar_predicao_expert(gc, gf)
    fig = px.pie(values=prob, names=['Empate', 'Casa', 'Fora'], hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- BUSCA REAL (API) ---
st.subheader("📅 Próximos Jogos")
if st.button("🔄 Buscar Jogos da API"):
    if not api_key:
        st.error("Coloque a API Key na lateral!")
    else:
        # Tenta temporada 2024 primeiro (mais comum para Brasileirão agora)
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {'x-apisports-key': api_key}
        params = {"league": liga_id, "season": 2026, "next": 10} 

        
        try:
            res = requests.get(url, headers=headers, params=params)
            jogos = res.json().get('response', [])
            
            if not jogos:
                st.warning("Nenhum jogo encontrado. Tente mudar a temporada para 2025 no código.")
            
            for j in jogos:
                casa = j['teams']['home']['name']
                fora = j['teams']['away']['name']
                prob_j = realizar_predicao_expert(1.5, 1.1)
                
                with st.expander(f"{casa} vs {fora}"):
                    st.write(f"Data: {j['fixture']['date'][:10]}")
                    st.write(f"🏠 Casa: {prob_j[1]*100:.1f}% | 🤝 Empate: {prob_j[0]*100:.1f}% | 🚀 Fora: {prob_j[2]*100:.1f}%")
        except Exception as e:
            st.error(f"Erro: {e}")
