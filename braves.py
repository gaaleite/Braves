import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Gráfico de Jogos")

# LINK OFICIAL DA SUA PLANILHA RESTAURADO
URL_NORMAL = "https://google.com"

@st.cache_data(ttl=10)
def carregar_dados_limpos(url):
    try:
        # Lê o CSV ignorando linhas de erro comuns do Google Sheets
        df = pd.read_csv(url, on_bad_lines='skip')
        
        if not df.empty:
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
            
            # FILTRO CRUCIAL ANTI-ERRO: Mantém apenas onde há dados na coluna K e L
            # Isso joga fora qualquer linha fantasma com código de Javascript do Google
            qtd_col = len(df.columns)
            if qtd_col >= 12:
                df.rename(columns={df.columns[10]: "PP", df.columns[11]: "PC"}, inplace=True)
                
                # Força a conversão das colunas de pontos e remove tudo o que for inválido
                df["PP"] = pd.to_numeric(df["PP"], errors='coerce')
                df["PC"] = pd.to_numeric(df["PC"], errors='coerce')
                
                # Remove linhas onde os pontos ficaram vazios/nulos (evita deformar o gráfico)
                df = df.dropna(subset=["PP", "PC"])
                
                # Mapeia os índices de texto que você listou
                if qtd_col >= 4:
                    df.rename(columns={df.columns[3]: "JOGO"}, inplace=True)
                if qtd_col >= 5:
                    df.rename(columns={df.columns[4]: "TIME"}, inplace=True)
                if qtd_col >= 13:
                    df.rename(columns={df.columns[12]: "ADVERSARIO"}, inplace=True)
                    
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return pd.DataFrame()

# Executa a carga com a super limpeza ativada
df_jogos = carregar_dados_limpos(URL_NORMAL)

if not df_jogos.empty:
    st.write("### 📈 Linha de Tendência e Pontuação")
    
    # Cria os nomes das partidas limpando nulos
    jogo_str = df_jogos["JOGO"].astype(str).str.strip()
    time_str = df_jogos["TIME"].astype(str).str.strip()
    adv_str = df_jogos["ADVERSARIO"].astype(str).str.strip()
    
    df_jogos["Partida"] = "J" + jogo_str + " - " + time_str + " vs " + adv_str
    
    # SEGURANÇA VISUAL: Remove textos com códigos conhecidos (ex: contendo 'var e' ou '{')
    df_jogos = df_jogos[~df_jogos["Partida"].str.contains(r"\{|function|var", case=False, na=True)]
    
    # GERAÇÃO DO GRÁFICO SEGURO
    fig = px.line(
        df_jogos,
        x="Partida",
        y=["PP", "PC"],
        title="Evolução de Pontos Feitos (PP) vs Pontos Sofridos (PC)",
        color_discrete_map={"PP": "#2ecc71", "PC": "#e74c3c"},
        markers=True,
        labels={"value": "Pontuação", "Partida": "Histórico de Jogos", "variable": "Indicador"}
    )
    
    # Ajusta as legendas laterais
    newnames = {'PP': 'Pontos Pró (PP)', 'PC': 'Pontos Contra (PC)'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aguardando carregamento correto dos dados da planilha...")
