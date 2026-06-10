import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# =========================================================================
# LINK OFICIAL DA SUA PLANILHA
# =========================================================================
URL_LEITURA_CSV = "https://google.com"
# =========================================================================

@st.cache_data(ttl=5)
def carregar_dados_posicionais(url):
    try:
        # Lê o CSV bruto sem assumir nenhuma linha como cabeçalho de texto fixo
        df = pd.read_csv(url, header=None, on_bad_lines='skip')
        if not df.empty:
            df_limpo = pd.DataFrame()
            
            # --- MAPEAMENTO POR ÍNDICES CRUS DAS COLUNAS (A=0, B=1, C=2...) ---
            # Filtramos e atribuímos apenas se a linha possuir dados suficientes
            df_limpo["ID_JOGO"] = df.iloc[:, 0].astype(str).str.strip()       # Coluna A (Ex: 277)
            df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()          # Coluna B (Ex: 07/06/2026)
            df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()           # Coluna C (Ex: 2026)
            df_limpo["TORNEIO"] = df.iloc[:, 3].astype(str).str.strip()       # Coluna D (Ex: Amistoso)
            df_limpo["CATEGORIA"] = df.iloc[:, 4].astype(str).str.strip()      # Coluna E (Ex: Adulto)
            df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()         # Coluna G (Ex: São Paulo)
            df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()         # Coluna H (Ex: SP)
            df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip() # Coluna I (Ex: V)
            
            # Colunas de Pontuação Tratadas Numericamente de Forma Segura (K=10 e L=11)
            df_limpo["PP"] = pd.to_numeric(df.iloc[:, 10], errors='coerce').fillna(0).astype(int)
            df_limpo["PC"] = pd.to_numeric(df.iloc[:, 11], errors='coerce').fillna(0).astype(int)
            
            df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()    # Coluna M (Ex: Crimson Fox)
            
            # --- LIMPEZA DE LINHAS INSTITUCIONAIS ---
            # Mantém apenas linhas onde a primeira coluna seja um número de jogo válido (ex: '277', '276')
            df_limpo = df_limpo[df_limpo["ID_JOGO"].str.isnumeric()]
            
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
        
        # Corta a string da data para obter o mês (ex: '07/06/2026' -> '06/2026')
        df_filtrado["Periodo"] = df_filtrado["DATA"].str.slice(3, 5) + "/" + df_filtrado["ANO"]
        
        # Consolida para o formato agrupado do gráfico do print
        df_agrupado = df_filtrado.groupby("Periodo").agg(
            Qtd_Jogos=("ID_JOGO", "count"),
            Media_PP=("PP", "mean")
        ).reset_index()
        
        # Ordena cronologicamente invertido ou normal se necessário
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
        
        # Linha de tendência escura cruzando por cima (Igual ao print)
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
