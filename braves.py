import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# =========================================================================
# LINK OFICIAL DA SUA PLANILHA (IDs ajustados para exportação direta)
# =========================================================================
URL_LEITURA_CSV = "https://docs.google.com/spreadsheets/d/1ZOetHxxdpHmPe2aCfPvli51YxXgD0LcFIVUEFIT6sDg/edit?gid=0#gid=0"
# =========================================================================

@st.cache_data(ttl=5)
def carregar_dados_posicionais(url):
    try:
        # Carrega a planilha sem assumir nenhuma linha fixa como cabeçalho de texto
        df = pd.read_csv(url, header=None, on_bad_lines='skip')
        if not df.empty:
            qtd_colunas = len(df.columns)
            df_limpo = pd.DataFrame()
            
            # --- MAPEAMENTO SEGURO POR ÍNDICES CRUS (A=0, B=1, C=2...) ---
            if qtd_colunas >= 1:   df_limpo["ID_JOGO"] = df.iloc[:, 0].astype(str).str.strip()
            if qtd_colunas >= 2:   df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()
            if qtd_colunas >= 3:   df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()
            if qtd_colunas >= 4:   df_limpo["TORNEIO"] = df.iloc[:, 3].astype(str).str.strip()
            if qtd_colunas >= 5:   df_limpo["CATEGORIA"] = df.iloc[:, 4].astype(str).str.strip()
            if qtd_colunas >= 7:   df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()
            if qtd_colunas >= 8:   df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()
            if qtd_colunas >= 9:   df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip()
            
            # Captura os campos de pontuação como texto para realizar a higienização contra ruídos literais
            if qtd_colunas >= 11:  df_limpo["PP_RAW"] = df.iloc[:, 10].astype(str).str.strip()
            if qtd_colunas >= 12:  df_limpo["PC_RAW"] = df.iloc[:, 11].astype(str).str.strip()
            if qtd_colunas >= 13:  df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()
            
            # --- FILTRAGEM E HIGIENIZAÇÃO DE TIPOS ---
            # Remove linhas de cabeçalho institucional textuais
            df_limpo = df_limpo[df_limpo["ID_JOGO"].str.isnumeric()]
            
            # Converte os campos de texto higienizados para inteiros numéricos finais
            df_limpo["PP"] = pd.to_numeric(df_limpo["PP_RAW"], errors='coerce').fillna(0).astype(int)
            df_limpo["PC"] = pd.to_numeric(df_limpo["PC_RAW"], errors='coerce').fillna(0).astype(int)
            
            # Elimina colunas temporárias de processamento bruto
            df_limpo = df_limpo.drop(columns=["PP_RAW", "PC_RAW"])
            
            return df_limpo.reset_index(drop=True)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar dados da tabela: {e}")
        return pd.DataFrame()

df_jogos = carregar_dados_posicionais(URL_LEITURA_CSV)

if not df_jogos.empty:
    st.write("### 🔍 Filtros de Pesquisa")
    
    # Grid de Filtros
    f1, f2, f3 = st.columns(3)
    busca_data = f1.text_input("🗓 Data", placeholder="Ex: 07/06", key="f_data").strip()
    busca_ano = f2.text_input("📆 Ano", placeholder="Ex: 2026", key="f_ano").strip()
    busca_categoria = f3.text_input("🛡️ Categoria", placeholder="Ex: Adulto", key="f_cat").strip()
    
    f4, f5, f6 = st.columns(3)
    busca_cidade = f4.text_input("📍 Nossa Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: Locomotives", key="f_adv").strip()
    busca_vd = f6.text_input("🏆 Resultados (V / D / E)", placeholder="Ex: V", key="f_vd").strip()
    
    # Filtragem dinâmica em tempo real
    df_filtrado = df_jogos.copy()
    if busca_data:
        df_filtrado = df_filtrado[df_filtrado["DATA"].str.contains(busca_data, na=False)]
    if busca_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO"].str.contains(busca_ano, na=False)]
    if busca_categoria:
        df_filtrado = df_filtrado[df_filtrado["CATEGORIA"].str.upper().str.contains(busca_categoria.upper(), na=False)]
    if busca_cidade:
        df_filtrado = df_filtrado[df_filtrado["CIDADE"].str.upper().str.contains(busca_cidade.upper(), na=False)]
    if busca_adversario:
        df_filtrado = df_filtrado[df_filtrado["ADVERSARIO"].str.upper().str.contains(busca_adversario.upper(), na=False)]
    if busca_vd:
        df_filtrado = df_filtrado[df_filtrado["VD"].str.upper().str.contains(busca_vd.upper(), na=False)]
        
    st.markdown("---")
    
    if not df_filtrado.empty:
        df_filtrado = df_filtrado.reset_index(drop=True)
        
        # --- BLOCO DE MÉTRICAS ESTILO DASHBOARD DO PRINT ---
        st.write("### 📊 Indicadores Gerais")
        m1, m2, m3 = st.columns(3)
        
        total_jogos = len(df_filtrado)
        total_pp = int(df_filtrado["PP"].sum())
        total_pc = int(df_filtrado["PC"].sum())
        
        m1.metric(label="Total de Partidas", value=f"{total_jogos}", delta=f"De {len(df_jogos)} registradas")
        m2.metric(label="Pontos Pró Acumulados (PP)", value=f"{total_pp}", delta="Pontos Feitos")
        m3.metric(label="Pontos Contra Acumulados (PC)", value=f"{total_pc}", delta="- Pontos Sofridos", delta_color="inverse")
        
        st.markdown("---")
        
        # --- CONSTRUÇÃO DO GRÁFICO (BARRAS AGRUPADAS POR MES/ANO) ---
        st.write("### 📈 Histórico Dinâmico de Atividade")
        
        # Ajusta a string da data de forma segura para criar a linha do tempo agrupada (Mês/Ano)
        df_filtrado["Periodo"] = df_filtrado["DATA"].str.slice(3, 5) + "/" + df_filtrado["ANO"]
        
        df_agrupado = df_filtrado.groupby("Periodo").agg(
            Qtd_Jogos=("ID_JOGO", "count"),
            Media_PP=("PP", "mean")
        ).reset_index()
        
        df_agrupado = df_agrupado.sort_values("Periodo")
        
        fig = go.Figure()
        
        # Barras de volume de partidas (Igual ao print)
        fig.add_trace(go.Bar(
            name="Volume de Jogos",
            x=df_agrupado["Periodo"],
            y=df_agrupado["Qtd_Jogos"],
            marker_color='#7cb5ec',
            text=df_agrupado["Qtd_Jogos"],
            textposition='auto',
            hovertemplate="Período: %{x}<br>Jogos Realizados: %{y}<extra></extra>"
        ))
        
        # Linha de tendência de desempenho (Igual ao print)
        fig.add_trace(go.Scatter(
            name="Tendência de Pontos Pró (Média PP)",
            x=df_agrupado["Periodo"],
            y=df_agrupado["Media_PP"],
            mode='lines+markers',
            line=dict(color='#2c3e50', width=2, dash='dash'),
            marker=dict(size=6, color='#2c3e50'),
            hovertemplate="Média PP: %{y:.1f}<extra></extra>"
        ))
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=80),
            xaxis=dict(showgrid=True, gridcolor='#f5f5f5', title="Meses / Anos de Competição"),
            yaxis=dict(showgrid=True, gridcolor='#f5f5f5', title="Escala")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado corresponde aos filtros aplicados nas caixas de pesquisa.")
else:
    st.error("Erro crítico: Verifique se o link da planilha está publicado como CSV para a web.")
