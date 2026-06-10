import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# =========================================================================
# CONFIGURAÇÃO DOS LINKS - INSIRA OS SEUS LINKS AQUI
# =========================================================================
URL_LEITURA_CSV = "https://docs.google.com/spreadsheets/d/1ZOetHxxdpHmPe2aCfPvli51YxXgD0LcFIVUEFIT6sDg/edit?gid=0#gid=0"
# =========================================================================

@st.cache_data(ttl=5)
def carregar_dados_posicionais(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        if not df.empty:
            qtd_colunas = len(df.columns)
            df_limpo = pd.DataFrame()
            
            # Mapeamento por índices físicos do ecossistema Braves
            if qtd_colunas >= 2:   df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()
            if qtd_colunas >= 3:   df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()
            if qtd_colunas >= 4:   df_limpo["JOGO"] = df.iloc[:, 3].astype(str).str.strip()
            if qtd_colunas >= 5:   df_limpo["TIME"] = df.iloc[:, 4].astype(str).str.strip()
            if qtd_colunas >= 7:   df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()
            if qtd_colunas >= 8:   df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()
            if qtd_colunas >= 9:   df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip()
            
            if qtd_colunas >= 11:  df_limpo["PP"] = pd.to_numeric(df.iloc[:, 10], errors='coerce').fillna(0)
            if qtd_colunas >= 12:  df_limpo["PC"] = pd.to_numeric(df.iloc[:, 11], errors='coerce').fillna(0)
            if qtd_colunas >= 13:  df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()
            
            # Limpezas nativas anti-ruído
            df_limpo = df_limpo[~df_limpo["JOGO"].str.contains(r"\{|function|var|index|void|call|html", case=False, na=True)]
            df_limpo = df_limpo[df_limpo["JOGO"] != "nan"]
            df_limpo = df_limpo[df_limpo["JOGO"] != ""]
            
            return df_limpo.reset_index(drop=True)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_jogos = carregar_dados_posicionais(URL_LEITURA_CSV)

if not df_jogos.empty:
    st.write("### 🔍 Filtros de Pesquisa")
    
    # Grid de Filtros compacto na mesma tela
    f1, f2, f3 = st.columns(3)
    busca_data = f1.text_input("🗓 Data", placeholder="Ex: 12/05", key="f_data").strip()
    busca_ano = f2.text_input("📆 Ano", placeholder="Ex: 2025", key="f_ano").strip()
    busca_time = f3.text_input("🛡️ Categoria / Time", placeholder="Ex: Sub 14", key="f_time").strip()
    
    f4, f5, f6 = st.columns(3)
    busca_cidade = f4.text_input("📍 Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: Fox", key="f_adv").strip()
    busca_vd = f6.text_input("🏆 Resultados (V / D / E)", placeholder="Ex: V", key="f_vd").strip()
    
    # Aplicação dos filtros em tempo real
    df_filtrado = df_jogos.copy()
    if busca_data:
        df_filtrado = df_filtrado[df_filtrado["DATA"].str.upper().str.contains(busca_data.upper(), na=False)]
    if busca_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO"].str.upper().str.contains(busca_ano.upper(), na=False)]
    if busca_time:
        df_filtrado = df_filtrado[df_filtrado["TIME"].str.upper().str.contains(busca_time.upper(), na=False)]
    if busca_cidade:
        df_filtrado = df_filtrado[df_filtrado["CIDADE"].str.upper().str.contains(busca_cidade.upper(), na=False)]
    if busca_adversario:
        df_filtrado = df_filtrado[df_filtrado["ADVERSARIO"].str.upper().str.contains(busca_adversario.upper(), na=False)]
    if busca_vd:
        df_filtrado = df_filtrado[df_filtrado["VD"].str.upper().str.contains(busca_vd.upper(), na=False)]
        
    st.markdown("---")
    
    if not df_filtrado.empty:
        df_filtrado = df_filtrado.reset_index(drop=True)
        
        # --- BLOCO DE MÉTRICAS ESTILO CARD (IGUAL AO PRINT) ---
        st.write("### 📊 Indicadores Gerais")
        m1, m2, m3 = st.columns(3)
        
        total_jogos = len(df_filtrado)
        total_pp = int(df_filtrado["PP"].sum())
        total_pc = int(df_filtrado["PC"].sum())
        
        m1.metric(label="Total de Partidas Filtradas", value=f"{total_jogos}", delta=f"De {len(df_jogos)} totais")
        m2.metric(label="Pontos Pró Consolidados (PP)", value=f"{total_pp}", delta="Pontos Feitos", delta_color="normal")
        m3.metric(label="Pontos Contra Consolidados (PC)", value=f"{total_pc}", delta="- Pontos Sofridos", delta_color="inverse")
        
        st.markdown("---")
        
        # --- PREPARAÇÃO DOS DADOS PARA O GRÁFICO DE ALTA DENSIDADE ---
        # Criamos uma linha do tempo unificada (Data/Ano) para agrupar o volume e não quebrar o layout com 277 barras individuais
        df_filtrado["Periodo"] = df_filtrado["DATA"] + "/" + df_filtrado["ANO"]
        
        # Agrupamos por período contando a atividade de jogos e tirando a média/soma de pontos
        df_agrupado = df_filtrado.groupby("Periodo").agg(
            Qtd_Jogos=("JOGO", "count"),
            Media_PP=("PP", "mean"),
            Total_PC=("PC", "sum")
        ).reset_index()
        
        # --- CONSTRUÇÃO DO GRÁFICO AVANÇADO (BARRAS DE ATIVIDADE + LINHA TENDÊNCIA) ---
        st.write("### 📈 Histórico Dinâmico de Atividade (Agrupado por Período)")
        
        fig = go.Figure()
        
        # 1. Barras azuis translúcidas representando o volume/frequência de jogos no período (Igual ao print)
        fig.add_trace(go.Bar(
            name="Quantidade de Jogos",
            x=df_agrupado["Periodo"],
            y=df_agrupado["Qtd_Jogos"],
            marker_color='#7cb5ec',
            text=df_agrupado["Qtd_Jogos"],
            textposition='auto',
            hovertemplate="Período: %{x}<br>Total de Jogos: %{y}<extra></extra>"
        ))
        
        # 2. Linha de tendência escura cruzando as barras no topo para indicar evolução de performance (Igual ao print)
        fig.add_trace(go.Scatter(
            name="Média de Pontos Pró (PP)",
            x=df_agrupado["Periodo"],
            y=df_agrupado["Media_PP"],
            mode='lines+markers',
            line=dict(color='#2c3e50', width=2, dash='dash'),
            marker=dict(size=6, color='#2c3e50'),
            hovertemplate="Média PP: %{y:.1f}<extra></extra>"
        ))
        
        # Estilização profissional idêntica à do print fornecido
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=80),
            xaxis=dict(
                showgrid=True, 
                gridcolor='#f5f5f5', 
                tickangle=-45,
                title="Linha do Tempo (Data/Ano)"
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#f5f5f5',
                title="Volume"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado corresponde aos filtros aplicados nas caixas de pesquisa.")
else:
    st.warning("Não foi possível carregar os dados. Verifique a estrutura da planilha.")
