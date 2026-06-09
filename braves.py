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
            
            # MAPEAMENTO EXATO CORRIGIDO USANDO OS ÍNDICES EXATOS DA PLANILHA
            qtd_col = len(df.columns)
            novos_nomes = {}
            if qtd_col >= 2:   novos_nomes[df.columns[1]]  = "DATA_INTERNA"
            if qtd_col >= 3:   novos_nomes[df.columns[2]]  = "ANO_INTERNA"
            if qtd_col >= 4:   novos_nomes[df.columns[3]]  = "JOGO_INTERNA"
            if qtd_col >= 5:   novos_nomes[df.columns[4]]  = "TIME_INTERNA"
            if qtd_col >= 7:   novos_nomes[df.columns[6]]  = "CIDADE_INTERNA"
            if qtd_col >= 8:   novos_nomes[df.columns[7]]  = "ESTADO_INTERNA"
            if qtd_col >= 9:   novos_nomes[df.columns[8]]  = "VD_INTERNA"
            if qtd_col >= 11:  novos_nomes[df.columns[10]] = "PP_INTERNA"
            if qtd_col >= 12:  novos_nomes[df.columns[11]] = "PC_INTERNA"
            if qtd_col >= 13:  novos_nomes[df.columns[12]] = "ADVERSARIO_INTERNA"
            
            df.rename(columns=novos_nomes, inplace=True)
            
            # Converte os pontos para formato numérico
            df["PP_INTERNA"] = pd.to_numeric(df["PP_INTERNA"], errors='coerce').fillna(0)
            df["PC_INTERNA"] = pd.to_numeric(df["PC_INTERNA"], errors='coerce').fillna(0)
            
            # Cria o nome descritivo padrão do jogo para o Eixo X
            df["Partida"] = (
                "J" + df["JOGO_INTERNA"].astype(str).str.strip() + " - " + 
                df["TIME_INTERNA"].astype(str).str.strip() + " vs " + 
                df["ADVERSARIO_INTERNA"].astype(str).str.strip()
            )
            
            # Remove linhas que contenham erros de código de Javascript do Google Sheets
            df = df[~df["Partida"].str.contains(r"\{|function|var", case=False, na=True)]
            df = df[df["JOGO_INTERNA"].astype(str).str.strip() != "nan"]
            
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return pd.DataFrame()

# Executa a carga com a super limpeza ativa
df_jogos = carregar_dados_limpos(URL_NORMAL)

if not df_jogos.empty:
    st.write("### 🔍 Filtros de Pesquisa")
    st.caption("Deixe os campos em branco para ver todos os dados. O gráfico atualiza automaticamente ao digitar.")
    
    # --- ORGANIZAÇÃO DOS FILTROS ATUALIZADOS (SEM O FILTRO DE JOGO) ---
    f1, f2 = st.columns(2)
    busca_data = f1.text_input("🗓 Filtrar por Data", placeholder="Ex: 12/05", key="f_data").strip()
    busca_ano = f2.text_input("📆 Filtrar por Ano", placeholder="Ex: 2025", key="f_ano").strip()
    
    f3, f4, f5 = st.columns(3)
    busca_time = f3.text_input("🛡️ Filtrar por Categoria / Time", placeholder="Ex: Sub 14", key="f_time").strip()
    busca_cidade = f4.text_input("📍 Filtrar por Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
    busca_adversario = f5.text_input("⚔️ Filtrar por Adversário", placeholder="Ex: Fox", key="f_adv").strip()
    
    f6, f7, f8 = st.columns(3)
    busca_vd = f6.text_input("🏆 Resultado (V = Vitória, D = Derrota, E = Empate)", placeholder="Ex: V", key="f_vd").strip()
    busca_pp = f7.text_input("🟢 Pontos Feitos (Mínimo)", placeholder="Ex: 10", key="f_pp").strip()
    busca_pc = f8.text_input("🔴 Pontos Sofridos (Máximo)", placeholder="Ex: 20", key="f_pc").strip()
    
    # --- PROCESSAMENTO DOS FILTROS EM TEMPO REAL ---
    df_filtrado = df_jogos.copy()
    
    if busca_data:
        df_filtrado = df_filtrado[df_filtrado["DATA_INTERNA"].astype(str).str.upper().str.contains(busca_data.upper(), na=False)]
    if busca_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO_INTERNA"].astype(str).str.upper().str.contains(busca_ano.upper(), na=False)]
    if busca_time:
        df_filtrado = df_filtrado[df_filtrado["TIME_INTERNA"].astype(str).str.upper().str.contains(busca_time.upper(), na=False)]
    if busca_cidade:
        df_filtrado = df_filtrado[df_filtrado["CIDADE_INTERNA"].astype(str).str.upper().str.contains(busca_cidade.upper(), na=False)]
    if busca_adversario:
        df_filtrado = df_filtrado[df_filtrado["ADVERSARIO_INTERNA"].astype(str).str.upper().str.contains(busca_adversario.upper(), na=False)]
    if busca_vd:
        df_filtrado = df_filtrado[df_filtrado["VD_INTERNA"].astype(str).str.upper().str.contains(busca_vd.upper(), na=False)]
    
    if busca_pp:
        try: df_filtrado = df_filtrado[df_filtrado["PP_INTERNA"] >= float(busca_pp)]
        except: pass
    if busca_pc:
        try: df_filtrado = df_filtrado[df_filtrado["PC_INTERNA"] <= float(busca_pc)]
        except: pass
        
    st.markdown("---")
    
    # --- EXIBIÇÃO DO GRÁFICO DINÂMICO ---
    if not df_filtrado.empty:
        df_filtrado = df_filtrado.reset_index(drop=True)
        
        st.write("### 📈 Linha de Tendência e Pontuação")
        
        # GERAÇÃO DO GRÁFICO EM FORMATO DE LINHA CONTÍNUA
        fig = px.line(
            df_filtrado,
            x="Partida",
            y=["PP_INTERNA", "PC_INTERNA"],
            title="Evolução de Pontos Feitos (PP) vs Pontos Sofridos (PC)",
            color_discrete_map={"PP_INTERNA": "#2ecc71", "PC_INTERNA": "#e74c3c"},
            markers=True,
            labels={"value": "Pontuação", "Partida": "Histórico de Jogos", "variable": "Indicador"}
        )
        
        # Ajusta as legendas laterais
        newnames = {'PP_INTERNA': 'Pontos Pró (PP)', 'PC_INTERNA': 'Pontos Contra (PC)'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado corresponde aos filtros aplicados nas caixas de pesquisa.")
else:
    st.warning("Aguardando carregamento correto dos dados da planilha...")
