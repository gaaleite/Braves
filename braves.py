import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Gráfico de Jogos")

# LINK OFICIAL DA SUA PLANILHA RESTAURADO
URL_NORMAL = "https://google.com"

# Função auxiliar para encontrar a coluna real pelo nome (mesmo com maiúsculas/minúsculas)
def encontrar_coluna(df, palavras_chave, nome_padrao):
    for col in df.columns:
        nome_limpo = str(col).strip().lower()
        if any(pc in nome_limpo for pc in palavras_chave):
            return col
    return nome_padrao

@st.cache_data(ttl=10)
def carregar_dados_limpos(url):
    try:
        # Lê o CSV pulando linhas corrompidas do Sheets
        df = pd.read_csv(url, on_bad_lines='skip')
        
        if not df.empty:
            # Limpa espaços em branco dos títulos das colunas
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
            
            # MAPEAMENTO DINÂMICO POR PALAVRA-CHAVE (Evita ler colunas de código JavaScript)
            c_data = encontrar_coluna(df, ["data", "date"], "DATA_REFEITO")
            c_ano = encontrar_coluna(df, ["ano", "year"], "ANO_REFEITO")
            c_jogo = encontrar_coluna(df, ["jogo", "game", "nº", "numero"], "JOGO_REFEITO")
            c_time = encontrar_coluna(df, ["time", "team", "categoria"], "TIME_REFEITO")
            c_cidade = encontrar_coluna(df, ["cidade", "city"], "CIDADE_REFEITO")
            c_estado = encontrar_coluna(df, ["estado", "state"], "ESTADO_REFEITO")
            c_vd = encontrar_coluna(df, ["v / d", "v/d", "resultado", "status"], "VD_REFEITO")
            c_pp = encontrar_coluna(df, ["pp", "pontos pró", "pontos pro", "pro"], "PP_REFEITO")
            c_pc = encontrar_coluna(df, ["pc", "pontos contra", "contra"], "PC_REFEITO")
            c_adv = encontrar_coluna(df, ["adversario", "adversário", "opponent"], "ADVERSARIO_REFEITO")
            
            # Cria um novo DataFrame apenas com as colunas mapeadas e limpas
            df_novo = pd.DataFrame()
            df_novo["DATA"] = df[c_data].astype(str).str.strip() if c_data in df.columns else ""
            df_novo["ANO"] = df[c_ano].astype(str).str.strip() if c_ano in df.columns else ""
            df_novo["JOGO"] = df[c_jogo].astype(str).str.strip() if c_jogo in df.columns else ""
            df_novo["TIME"] = df[c_time].astype(str).str.strip() if c_time in df.columns else ""
            df_novo["CIDADE"] = df[c_cidade].astype(str).str.strip() if c_cidade in df.columns else ""
            df_novo["ESTADO"] = df[c_estado].astype(str).str.strip() if c_estado in df.columns else ""
            df_novo["VD"] = df[c_vd].astype(str).str.upper().str.strip() if c_vd in df.columns else ""
            df_novo["ADVERSARIO"] = df[c_adv].astype(str).str.strip() if c_adv in df.columns else ""
            
            # Tratamento numérico rigoroso das colunas de pontos (K e L)
            df_novo["PP"] = pd.to_numeric(df[c_pp], errors='coerce').fillna(0) if c_pp in df.columns else 0
            df_novo["PC"] = pd.to_numeric(df[c_pc], errors='coerce').fillna(0) if c_pc in df.columns else 0
            
            # Filtro de segurança: Remove linhas com códigos, links ou textos inválidos
            df_novo = df_novo[~df_novo["JOGO"].str.contains(r"\{|function|var|index|void|call", case=False, na=True)]
            df_novo = df_novo[~df_novo["TIME"].str.contains(r"\{|function|var|index|void|call", case=False, na=True)]
            df_novo = df_novo[df_novo["JOGO"] != "nan"]
            df_novo = df_novo[df_novo["JOGO"] != ""]
            
            return df_novo.reset_index(drop=True)
            
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na conexão com os dados: {e}")
        return pd.DataFrame()

# Carrega a base de dados tratada
df_jogos = carregar_dados_limpos(URL_NORMAL)

if not df_jogos.empty:
    st.write("### 🔍 Filtros de Pesquisa")
    st.caption("Deixe os campos em branco para ver todos os dados da linha do tempo.")
    
    # --- FILTROS DE TEXTO ATUALIZADOS (PONTOS REMOVIDOS) ---
    f1, f2 = st.columns(2)
    busca_data = f1.text_input("🗓 Filtrar por Data", placeholder="Ex: 12/05", key="f_data").strip()
    busca_ano = f2.text_input("📆 Filtrar por Ano", placeholder="Ex: 2025", key="f_ano").strip()
    
    f3, f4, f5 = st.columns(3)
    busca_time = f3.text_input("🛡️ Filtrar por Categoria / Time", placeholder="Ex: Sub 14", key="f_time").strip()
    busca_cidade = f4.text_input("📍 Filtrar por Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
    busca_adversario = f5.text_input("⚔️ Filtrar por Adversário", placeholder="Ex: Fox", key="f_adv").strip()
    
    f6 = st.columns(1)[0]
    busca_vd = f6.text_input("🏆 Resultado (V = Vitória, D = Derrota, E = Empate)", placeholder="Ex: V", key="f_vd").strip()
    
    # --- PROCESSAMENTO DOS FILTROS EM TEMPO REAL ---
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
    
    # --- RENDEREZAÇÃO DO GRÁFICO SEGURO ---
    if not df_filtrado.empty:
        df_filtrado = df_filtrado.reset_index(drop=True)
        
        st.write("### 📈 Linha de Tendência e Pontuação")
        
        # Reconstrói a legenda do Eixo X usando os textos limpos da planilha
        df_filtrado["Partida"] = (
            "J" + df_filtrado["JOGO"] + " - " + 
            df_filtrado["TIME"] + " vs " + 
            df_filtrado["ADVERSARIO"]
        )
        
        # Gráfico de linha puro
        fig = px.line(
            df_filtrado,
            x="Partida",
            y=["PP", "PC"],
            title="Evolução de Pontos Feitos (PP) vs Pontos Sofridos (PC)",
            color_discrete_map={"PP": "#2ecc71", "PC": "#e74c3c"},
            markers=True,
            labels={"value": "Pontuação", "Partida": "Histórico de Jogos", "variable": "Indicador"}
        )
        
        # Altera os nomes exibidos na legenda lateral
        newnames = {'PP': 'Pontos Pró (PP)', 'PC': 'Pontos Contra (PC)'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado corresponde aos filtros aplicados nas caixas de pesquisa.")
else:
    st.warning("Aguardando carregamento correto dos dados da planilha...")
