import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GolBetPro AI", page_icon="⚽")

# --- FUNÇÃO DA IA (PREDIÇÃO) ---
import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px # Para gráficos bonitos

# --- NOVA FUNÇÃO DE IA EXPERT ---
def treinar_e_prever(gols_c, gols_f):
    try:
        # Tenta carregar seu banco de dados de milhares de jogos
        df = pd.read_csv('historico_jogos.csv')
        X = df[['media_gols_casa', 'media_gols_fora']]
        y = df['resultado']
        
        modelo = RandomForestClassifier(n_estimators=200)
        modelo.fit(X, y)
        
        # Faz a previsão baseada nos dados que você inseriu
        probabilidades = modelo.predict_proba([[gols_c, gols_f]])[0]
        return probabilidades
    except:
        # Caso o arquivo ainda não exista, retorna uma probabilidade padrão
        return [0.33, 0.33, 0.34] 

# --- PARTE DO CÓDIGO QUE EXIBE O GRÁFICO ---
st.subheader("📊 Probabilidades da IA")
prob = treinar_e_prever(gc, gf) # gc e gf são as entradas de gols

# Criando um gráfico de pizza para o seu iPhone
labels = ['Empate', 'Vitória Casa', 'Vitória Fora']
fig = px.pie(values=prob, names=labels, color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig, use_container_width=True)


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
