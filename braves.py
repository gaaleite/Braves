import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Gráfico de Jogos")

# LINK OFICIAL DA SUA PLANILHA
URL_NORMAL = "https://google.com"

@st.cache_data(ttl=10)
def carregar_dados_posicionais(url):
    try:
        # Lê o CSV sem assumir cabeçalhos fixos para evitar conflito com scripts ocultos
        df = pd.read_csv(url, on_bad_lines='skip')
        
        if not df.empty:
            qtd_colunas = len(df.columns)
            
            # Criamos um DataFrame totalmente limpo usando os índices informados por você (ajustados para começarem do 0)
            df_limpo = pd.DataFrame()
            
            # Mapeamento exato das colunas fornecidas:
            if qtd_colunas >= 2:   df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()       # 2ª coluna
            if qtd_colunas >= 3:   df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()        # 3ª coluna
            if qtd_colunas >= 4:   df_limpo["JOGO"] = df.iloc[:, 3].astype(str).str.strip()       # 4ª coluna
            if qtd_colunas >= 5:   df_limpo["TIME"] = df.iloc[:, 4].astype(str).str.strip()       # 5ª coluna
            if qtd_colunas >= 7:   df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()     # 7ª coluna
            if qtd_colunas >= 8:   df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()     # 8ª coluna
            if qtd_colunas >= 9:   df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip() # 9ª coluna
            
            # Colunas de Pontuação (11ª e 12ª) - Tratadas como números diretamente
            if qtd_colunas >= 11:  df_limpo["PP"] = pd.to_numeric(df.iloc[:, 10], errors='coerce').fillna(0)
            if qtd_colunas >= 12:  df_limpo["PC"] = pd.to_numeric(df.iloc[:, 11], errors='coerce').fillna(0)
            
            if qtd_colunas >= 13:  df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip() # 13ª coluna
            
            # --- LIMPEZA DE SEGURANÇA CONTRA CÓDIGOS DO GOOGLE ---
            # Remove linhas que contenham fragmentos de código Javascript gerados pelo Sheets
            df_limpo = df_limpo[~df_limpo["JOGO"].str.contains(r"\{|function|var|index|void|call|html", case=False, na=True)]
            df_limpo = df_limpo[~df_limpo["TIME"].str.contains(r"\{|function|var|index|void|call|html", case=False, na=True)]
            
            # Remove linhas vazias ou nulas no identificador principal
            df_limpo = df_limpo[df_limpo["JOGO"] != "nan"]
            df_limpo = df_limpo[df_limpo["JOGO"] != ""]
            
            return df_limpo.reset_index(drop=True)
            
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na conexão com os dados: {e}")
        return pd.DataFrame()

# Carrega a base tratada por índices físicos
df_jogos = carregar_dados_posicionais(URL_NORMAL)

if not df_jogos.empty:
    st.write("### 🔍 Filtros de Pesquisa")
    st.caption("Deixe os campos em branco para ver todos os dados da linha do tempo.")
    
    # --- ORGANIZAÇÃO DOS FILTROS (SEM A PALAVRA 'FILTRAR') ---
    f1, f2 = st.columns(2)
    busca_data = f1.text_input("🗓 Data", placeholder="Ex: 12/05", key="f_data").strip()
    busca_ano = f2.text_input("📆 Ano", placeholder="Ex: 2025", key="f_ano").strip()
    
    f3, f4, f5 = st.columns(3)
    busca_time = f3.text_input("🛡️ Categoria / Time", placeholder="Ex: Sub 14", key="f_time").strip()
    busca_cidade = f4.text_input("📍 Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: Fox", key="f_adv").strip()
    
    # NOVO NOME SOLICITADO
    f6_col, = st.columns(1)
    busca_vd = f6_col.text_input("🏆 Resultados (V / D / E)", placeholder="Ex: V", key="f_vd").strip()
    
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
    
    # --- RENDERIZAÇÃO DO GRÁFICO DINÂMICO ---
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
    st.warning("Não foi possível carregar os dados. Verifique se as colunas da planilha seguem a ordem correta.")
