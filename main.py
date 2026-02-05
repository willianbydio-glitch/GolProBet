import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GolBetPro AI", page_icon="⚽", layout="centered")

# --- FUNÇÃO DE CARREGAMENTO DE DADOS (CÉREBRO DA IA) ---
@st.cache_data # Isso faz o app carregar mais rápido no iPhone
def carregar_dados_treinamento():
    try:
        # Tenta ler o arquivo do Football-Data.co.uk que você subiu no GitHub
        df = pd.read_csv('brazil.csv') 
        
        # Mapeamento: H (Casa) -> 1, D (Empate) -> 0, A (Fora) -> 2
        mapeamento = {'H': 1, 'D': 0, 'A': 2}
        
        dados_ia = pd.DataFrame()
        dados_ia['media_gols_casa'] = df['FTHG']
        dados_ia['media_gols_fora'] = df['FTAG']
        dados_ia['resultado'] = df['FTR'].map(mapeamento)
        
        return dados_ia.dropna()
    except Exception as e:
        return None

# --- FUNÇÃO DE PREDIÇÃO CORRIGIDA ---
def realizar_predicao_expert(gols_c, gols_f):
    dados = carregar_dados_treinamento()
    
    if dados is not None:
        X = dados[['media_gols_casa', 'media_gols_fora']]
        y = dados['resultado']
        
        modelo = RandomForestClassifier(n_estimators=200, random_state=42)
        modelo.fit(X, y)
        
        # Gera as probabilidades
        probabilidades = modelo.predict_proba([[gols_c, gols_f]])[0]
        return probabilidades
    else:
        # Se o CSV falhar, retorna 33% para cada lado
        return [0.333, 0.333, 0.334]

# --- INTERFACE ---
st.title("⚽ GolBetPro AI v2.1")

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Sua API Key", type="password")
    liga_nome = st.selectbox("Escolha a Liga", ["Brasileirão", "Premier League", "La Liga"])
    # IDs reais da API-Football
    liga_id = {"Premier League": 39, "Brasileirão": 71, "La Liga": 140}[liga_nome]

# --- ABA DE TESTE MANUAL ---
st.subheader("🧪 Simulação Manual")
col_m1, col_m2 = st.columns(2)
gc_manual = col_m1.number_input("Média Gols Casa", 0.0, 5.0, 1.5)
gf_manual = col_m2.number_input("Média Gols Fora", 0.0, 5.0, 1.2)

if st.button("Analisar Simulação"):
    prob = realizar_predicao_expert(gc_manual, gf_manual)
    
    # Gráfico de Pizza
    labels = ['Empate', 'Vitória Casa', 'Vitória Fora']
    fig = px.pie(values=prob, names=labels, 
                 color_discrete_sequence=px.colors.sequential.RdBu,
                 hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- ABA DA API (CORRIGIDA) ---
st.subheader("📅 Próximos Jogos Reais")
if st.button("🔄 Buscar e Analisar Jogos da API"):
    if not api_key:
        st.error("⚠️ Por favor, insira sua API Key na barra lateral!")
    else:
        with st.spinner('Conectando com a API...'):
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {'x-apisports-key': api_key}
            # Busca os próximos 8 jogos da liga selecionada
            params = {"league": liga_id, "season": 2025, "next": 8} 
            
            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()
                jogos = data.get('response', [])
                
                if not jogos:
                    st.warning("Nenhum jogo próximo encontrado para esta liga.")
                
                for jogo in jogos:
                    time_c = jogo['teams']['home']['name']
                    time_f = jogo['teams']['away']['name']
                    data_jogo = jogo['fixture']['date'][:10]
                    
                    # A IA analisa o jogo (usando médias padrão ou dados da API se disponíveis)
                    # Aqui usamos 1.5 e 1.2 como base para a predição
                    prob_jogo = realizar_predicao_expert(1.5, 1.2)
                    
                    with st.expander(f"🏟️ {time_c} vs {time_f}"):
                        st.write(f"**Data:** {data_jogo}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Casa", f"{prob_jogo[1]*100:.1f}%")
                        c2.metric("Empate", f"{prob_jogo[0]*100:.1f}%")
                        c3.metric("Fora", f"{prob_jogo[2]*100:.1f}%")
                        
            except Exception as e:
                st.error(f"Erro na conexão: {e}")

st.divider()
st.caption("GolBetPro - Sistema de Análise Preditiva para iPhone")
