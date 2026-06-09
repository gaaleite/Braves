import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")

st.title("🏈 Braves Academy - Gerenciador de Jogos")

# LINK OFICIAL: Exporta diretamente os dados limpos da planilha
URL_NORMAL = "https://google.com"

# -------------------------------------------------------------------------
# FUNÇÃO DE LEITURA DIRETA DO GOOGLE SHEETS
# -------------------------------------------------------------------------
@st.cache_data(ttl=10) # Atualiza automaticamente a cada 10 segundos
def carregar_aba_google(url_planilha):
    try:
        df = pd.read_csv(url_planilha)
        if not df.empty:
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return pd.DataFrame()

# -------------------------------------------------------------------------
# FUNÇÃO PARA COLORIR AS LINHAS DA TABELA BASEADO NA COLUNA "V / D"
# -------------------------------------------------------------------------
def colorir_linhas(linha):
    resultado = str(linha["V / D"]).strip().upper() if "V / D" in linha else ""
    
    # Define as cores de fundo em formato RGBA/Hex aceito pelo Pandas/Streamlit
    if resultado == "V":
        return ["background-color: rgba(46, 204, 113, 0.25)"] * len(linha)  # Verde Claro
    elif resultado == "D":
        return ["background-color: rgba(231, 76, 60, 0.25)"] * len(linha)   # Vermelho Claro
    elif resultado == "E":
        return ["background-color: rgba(241, 196, 15, 0.25)"] * len(linha)  # Amarelo Claro
    return [""] * len(linha)

# -------------------------------------------------------------------------
# GERENCIAMENTO DOS DADOS EM MEMÓRIA
# -------------------------------------------------------------------------
if "lista_abas" not in st.session_state:
    st.session_state.lista_abas = ["ALL GAMES"]

# INTERFACE: ADICIONAR NOVA ABA
with st.expander("➕ Adicionar Nova Aba / Categoria"):
    nova_aba_input = st.text_input("Nome da nova aba:", placeholder="Ex: playoffs 25").strip()
    if st.button("Criar Aba"):
        if nova_aba_input and nova_aba_input not in st.session_state.lista_abas:
            st.session_state.lista_abas.append(nova_aba_input)
            st.success(f"Aba '{nova_aba_input}' criada com sucesso!")
            st.rerun()

# Criação visual das abas no navegador
tabs = st.tabs(st.session_state.lista_abas)

# Carrega os dados reais da planilha
df_todos_jogos = carregar_aba_google(URL_NORMAL)

# Renderizar o conteúdo de cada aba
for i, nome_da_aba in enumerate(st.session_state.lista_abas):
    with tabs[i]:
        st.subheader(nome_da_aba)
        
        if nome_da_aba == "ALL GAMES":
            if df_todos_jogos.empty:
                st.warning("Nenhum dado encontrado ou a planilha está inacessível. Verifique o compartilhamento.")
            else:
                st.write("### 🔍 Filtros de Pesquisa")
                st.caption("Digite nos campos abaixo. O gráfico e a tabela atualizarão instantaneamente.")
                
                # --- ORGANIZAÇÃO DOS FILTROS ---
                f1, f2, f3 = st.columns(3)
                busca_data = f1.text_input("🗓 Filtrar por Data", placeholder="Ex: 12/05", key="f_data").strip()
                busca_ano = f2.text_input("📆 Filtrar por Ano", placeholder="Ex: 2025", key="f_ano").strip()
                busca_jogo = f3.text_input("🏈 Filtrar por Jogo (Nº)", placeholder="Ex: 277", key="f_jogo").strip()
                
                f4, f5, f6 = st.columns(3)
                busca_time = f4.text_input("🛡️ Filtrar por Categoria / Time", placeholder="Ex: Sub 14", key="f_time").strip()
                busca_cidade = f5.text_input("📍 Filtrar por Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
                busca_adversario = f6.text_input("⚔️ Filtrar por Adversário", placeholder="Ex: Fox", key="f_adv").strip()
                
                f7, f8, f9 = st.columns(3)
                # O filtro abaixo agora centraliza as pesquisas de resultado (V, D ou E)
                busca_vd = f7.text_input("🏆 Resultado (V = Vitória, D = Derrota, E = Empate)", placeholder="Ex: V", key="f_vd").strip()
                busca_pp = f8.text_input("🟢 Pontos Feitos (Mínimo)", placeholder="Ex: 10", key="f_pp").strip()
                busca_pc = f9.text_input("🔴 Pontos Sofridos (Máximo)", placeholder="Ex: 20", key="f_pc").strip()
                
                # --- PROCESSAMENTO DOS FILTROS EM TEMPO REAL ---
                df_filtrado = df_todos_jogos.copy()
                
                if busca_data and "DATA" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["DATA"].astype(str).str.upper().str.contains(busca_data.upper(), na=False)]
                if busca_ano and "ANO" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["ANO"].astype(str).str.upper().str.contains(busca_ano.upper(), na=False)]
                if busca_jogo and "JOGO" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["JOGO"].astype(str).str.upper().str.contains(busca_jogo.upper(), na=False)]
                if busca_time and "TIME" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["TIME"].astype(str).str.upper().str.contains(busca_time.upper(), na=False)]
                if busca_cidade and "CIDADE" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["CIDADE"].astype(str).str.upper().str.contains(busca_cidade.upper(), na=False)]
                if busca_adversario and "ADVERSÁRIO" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["ADVERSÁRIO"].astype(str).str.upper().str.contains(busca_adversario.upper(), na=False)]
                if busca_vd and "V / D" in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado["V / D"].astype(str).str.upper().str.contains(busca_vd.upper(), na=False)]
                
                if busca_pp and "PP" in df_filtrado.columns:
                    df_filtrado["PP"] = pd.to_numeric(df_filtrado["PP"], errors='coerce').fillna(0)
                    try: df_filtrado = df_filtrado[df_filtrado["PP"] >= float(busca_pp)]
                    except: pass
                if busca_pc and "PC" in df_filtrado.columns:
                    df_filtrado["PC"] = pd.to_numeric(df_filtrado["PC"], errors='coerce').fillna(0)
                    try: df_filtrado = df_filtrado[df_filtrado["PC"] <= float(busca_pc)]
                    except: pass
                    
                st.markdown("---")
                
                # --- EXIBIÇÃO DOS RESULTADOS ---
                if not df_filtrado.empty:
                    df_filtrado = df_filtrado.reset_index(drop=True)
                    
                    # 1. Gráfico de Barras Dinâmico
                    st.write("### 📈 Gráfico de Pontuação das Partidas")
                    
                    df_filtrado["PP"] = pd.to_numeric(df_filtrado["PP"], errors='coerce').fillna(0)
                    df_filtrado["PC"] = pd.to_numeric(df_filtrado["PC"], errors='coerce').fillna(0)
                    
                    df_filtrado["Partida"] = (
                        "J" + df_filtrado["JOGO"].astype(str) + " - " +
                        df_filtrado["TIME"].astype(str) + " vs " +
                        df_filtrado["ADVERSÁRIO"].astype(str) + " (" + df_filtrado["V / D"].astype(str) + ")"
                    )
                    
                    fig = px.bar(
                        df_filtrado,
                        y="Partida",
                        x=["PP", "PC"],
                        orientation="h",
                        barmode="group",
                        title="Pontos Feitos (PP) vs Pontos Sofridos (PC)",
                        color_discrete_map={"PP": "#2ecc71", "PC": "#e74c3c"},
                        labels={"value": "Pontos", "variable": "Tipo de Ponto"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 2. Tabela Oficial Estilizada com Cores (Igual ao Sheets)
                    st.write("### 📋 Tabela de Registros")
                    
                    # Aplica a função de mapeamento de cores linha por linha
                    df_estilizado = df_filtrado.style.apply(colorir_linhas, axis=1)
                    
                    # Renderiza a tabela colorida na tela do app
                    st.dataframe(df_estilizado, use_container_width=True)
                else:
                    st.info("Nenhum dado corresponde aos filtros aplicados nas caixas de pesquisa.")
