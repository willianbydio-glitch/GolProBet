import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GolBetPro AI", page_icon="⚽")

# --- FUNÇÃO DE CARREGAMENTO (FOOTBALL-DATA.CO.UK) ---
def carregar_dados_treinamento():
    try:
        # Tenta ler o arquivo baixado do site (ex: brazil.csv)
        df = pd.read_csv('brazil.csv') 
        
        # Mapeamento das siglas do site para números
        # H (Home) -> 1, D (Draw) -> 0, A (Away) -> 2
        mapeamento = {'H': 1, 'D': 0, 'A': 2}
        
        dados_ia = pd.DataFrame()
        dados_ia['media_gols_casa'] = df['FTHG']
        dados_ia['media_gols_fora'] = df['FTAG']
        dados_ia['resultado'] = df['FTR'].map(mapeamento)
        
        # Remove linhas vazias caso existam
        return dados_ia.dropna()
    except Exception as e:
        st.error(f"Erro ao carregar brazil.csv: {e}")
        return None

# --- FUNÇÃO DA IA EXPERT ---
def treinar_e_prever(gols_c, gols_f):
    dados = carregar_dados_treinamento()
    
    if dados is not None:
        X = dados[['media_gols_casa', 'media_gols_fora']]
        y = dados['resultado']
        
        modelo = RandomForestClassifier(n_estimators=200, random_state=42)
        modelo.fit(X, y)
        
        # Predição de probabilidades
        probabilidades = modelo.predict_proba([[gols_c, gols_f]])[0]
        # Ordem das classes no modelo: 0 (Empate), 1 (Casa), 2 (Fora)
        return probabilidades
    else:
        return [0.33, 0.33, 0.34] # Retorno padrão caso falhe

# --- INTERFACE PRINCIPAL ---
st.title("⚽ GolBetPro Inteligência Artificial")

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Sua API Key", type="password")
    liga = st.selectbox("Escolha a Liga", ["Brasileirão", "Premier League", "La Liga"])
    liga_id = {"Premier League": 39, "Brasileirão": 71, "La Liga": 140}[liga]

# --- SEÇÃO DE TESTE MANUAL E GRÁFICO ---
st.subheader("🧪 Teste a IA Manualmente")
c1, c2 = st.columns(2)
gc = c1.number_input("Gols Médios Casa", 0.0, 5.0, 1.5)
gf = c2.number_input("Gols Médios Fora", 0.0, 5.0, 1.2)

if st.button("Calcular Probabilidade"):
    prob = treinar_e_prever(gc, gf)
    
    # Exibição do Gráfico de Pizza
    labels = ['Empate', 'Vitória Casa', 'Vitória Fora']
    fig = px.pie(values=prob, names=labels, 
                 title="Chances Calculadas pela IA",
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)
    
    # Resultado em texto
    vencedor_idx = prob.tolist().index(max(prob))
    nomes = ["Empate", "Vitória do Time da Casa", "Vitória do Visitante"]
    st.success(f"Palpite Principal: **{nomes[vencedor_idx]}** ({max(prob)*100:.1f}%)")

# --- LÓGICA DE BUSCA API ---
st.divider()
if st.button("🔄 Buscar e Analisar Próximos Jogos"):
    if not api_key:
        st.error("Insira sua API Key na lateral!")
    else:
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {'x-apisports-key': api_key}
        params = {"league": liga_id, "season": 2024, "next": 5}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            jogos = response.json().get('response', [])
            
            for jogo in jogos:
                casa = jogo['teams']['home']['name']
                fora = jogo['teams']['away']['name']
                
                # Para jogos da API, usamos a predição baseada no modelo
                # (Aqui usamos valores base 1.5 e 1.2 como exemplo)
                prob_jogo = treinar_e_prever(1.5, 1.2)
                
                with st.expander(f"{casa} vs {fora}"):
                    st.write(f"📅 Data: {jogo['fixture']['date'][:10]}")
                    st.write(f"🏠 Vitória Casa: {prob_jogo[1]*100:.1f}%")
                    st.write(f"🤝 Empate: {prob_jogo[0]*100:.1f}%")
                    st.write(f"🚀 Vitória Fora: {prob_jogo[2]*100:.1f}%")
        except Exception as e:
            st.error(f"Erro na API: {e}")

# --- ALIMENTAR DADOS ---
st.divider()
st.subheader("📝 Alimentar Inteligência")
with st.form("novo_dado"):
    st.write("Registre novos resultados para o banco de dados local")
    nc = st.number_input("Gols Casa", min_value=0.0)
    nf = st.number_input("Gols Fora", min_value=0.0)
    res_manual = st.selectbox("Resultado", ["H", "D", "A"])
    if st.form_submit_button("Registrar"):
        st.info("Dado registrado temporariamente. Para salvar permanentemente, atualize o arquivo 'brazil.csv' no GitHub.")
