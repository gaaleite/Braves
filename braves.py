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
            
            # MAPEAMENTO EXATO BASEADO NAS POSIÇÕES INFORMADAS
            qtd_colunas = len(df.columns)
            
            # Dicionário para renomear colunas por índice físico
            novos_nomes = {}
            if qtd_colunas >= 2:   novos_nomes[df.columns[1]]  = "DATA_INTERNA"
            if qtd_colunas >= 3:   novos_nomes[df.columns[2]]  = "ANO_INTERNA"
            if qtd_colunas >= 4:   novos_nomes[df.columns[3]]  = "JOGO_INTERNA"
            if qtd_colunas >= 5:   novos_nomes[df.columns[4]]  = "TIME_INTERNA"
            if qtd_colunas >= 7:   novos_nomes[df.columns[6]]  = "CIDADE_INTERNA"
            if qtd_colunas >= 8:   novos_nomes[df.columns[7]]  = "ESTADO_INTERNA"
            if qtd_colunas >= 9:   novos_nomes[df.columns[8]]  = "VD_INTERNA"
            if qtd_colunas >= 11:  novos_nomes[df.columns[10]] = "PP_INTERNA"
            if qtd_colunas >= 12:  novos_nomes[df.columns[11]] = "PC_INTERNA"
            if qtd_colunas >= 13:  novos_nomes[df.columns[12]] = "ADVERSARIO_INTERNA"
            
            df.rename(columns=novos_nomes, inplace=True)
                
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return pd.DataFrame()

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

# Nomes padronizados das variáveis internas
col_data = "DATA_INTERNA"
col_ano = "ANO_INTERNA"
col_jogo = "JOGO_INTERNA"
col_time = "TIME_INTERNA"
col_cidade = "CIDADE_INTERNA"
col_estado = "ESTADO_INTERNA"
col_vd = "VD_INTERNA"
col_pp = "PP_INTERNA"
col_pc = "PC_INTERNA"
col_adv = "ADVERSARIO_INTERNA"

colunas_finais = [col_data, col_ano, col_jogo, col_time, col_cidade, col_estado, col_vd, col_pp, col_pc, col_adv]

# Garante a existência das colunas para evitar falhas de compilação
for col in colunas_finais:
    if not df_todos_jogos.empty and col not in df_todos_jogos.columns:
        df_todos_jogos[col] = ""

# Renderizar o conteúdo de cada aba
for i, nome_da_aba in enumerate(st.session_state.lista_abas):
    with tabs[i]:
        st.subheader(nome_da_aba)
        
        if nome_da_aba == "ALL GAMES":
            if df_todos_jogos.empty:
                st.warning("Nenhum dado encontrado ou a planilha está inacessível. Verifique o compartilhamento.")
            else:
                st.write("### 🔍 Filtros de Pesquisa")
                st.caption("Deixe os campos em branco para ver todos os dados. Digite para filtrar em tempo real.")
                
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
                busca_vd = f7.text_input("🏆 Resultado (V = Vitória, D = Derrota, E = Empate)", placeholder="Ex: V", key="f_vd").strip()
                busca_pp = f8.text_input("🟢 Pontos Feitos (Mínimo)", placeholder="Ex: 10", key="f_pp").strip()
                busca_pc = f9.text_input("🔴 Pontos Sofridos (Máximo)", placeholder="Ex: 20", key="f_pc").strip()
                
                # --- PROCESSAMENTO DOS FILTROS EM TEMPO REAL ---
                df_filtrado = df_todos_jogos.copy()
                
                if busca_data and col_data in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_data].astype(str).str.upper().str.contains(busca_data.upper(), na=False)]
                if busca_ano and col_ano in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_ano].astype(str).str.upper().str.contains(busca_ano.upper(), na=False)]
                if busca_jogo and col_jogo in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_jogo].astype(str).str.upper().str.contains(busca_jogo.upper(), na=False)]
                if busca_time and col_time in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_time].astype(str).str.upper().str.contains(busca_time.upper(), na=False)]
                if busca_cidade and col_cidade in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_cidade].astype(str).str.upper().str.contains(busca_cidade.upper(), na=False)]
                if busca_adversario and col_adv in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_adv].astype(str).str.upper().str.contains(busca_adversario.upper(), na=False)]
                if busca_vd and col_vd in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado[col_vd].astype(str).str.upper().str.contains(busca_vd.upper(), na=False)]
                
                if busca_pp and col_pp in df_filtrado.columns:
                    df_filtrado[col_pp] = pd.to_numeric(df_filtrado[col_pp], errors='coerce').fillna(0)
                    try: df_filtrado = df_filtrado[df_filtrado[col_pp] >= float(busca_pp)]
                    except: pass
                if busca_pc and col_pc in df_filtrado.columns:
                    df_filtrado[col_pc] = pd.to_numeric(df_filtrado[col_pc], errors='coerce').fillna(0)
                    try: df_filtrado = df_filtrado[df_filtrado[col_pc] <= float(busca_pc)]
                    except: pass
                    
                st.markdown("---")
                
                # --- EXIBIÇÃO DOS RESULTADOS ---
                if not df_filtrado.empty:
                    df_filtrado = df_filtrado.reset_index(drop=True)
                    
                    st.write("### 📈 Linha de Tendência e Pontuação")
                    
                    # Converte os pontos para formato numérico
                    df_filtrado[col_pp] = pd.to_numeric(df_filtrado[col_pp], errors='coerce').fillna(0)
                    df_filtrado[col_pc] = pd.to_numeric(df_filtrado[col_pc], errors='coerce').fillna(0)
                    
                    # Constrói o texto identificador de cada jogo no eixo X de forma limpa
                    df_filtrado["Partida"] = (
                        "J" + df_filtrado[col_jogo].astype(str) + " - " +
                        df_filtrado[col_time].astype(str) + " vs " +
                        df_filtrado[col_adv].astype(str)
                    )
                    
                    # Criação do gráfico em formato de linha contínua
                    fig = px.line(
                        df_filtrado,
                        x="Partida",
                        y=[col_pp, col_pc],
                        title="Evolução de Pontos Feitos (PP) vs Pontos Sofridos (PC)",
                        color_discrete_map={col_pp: "#2ecc71", col_pc: "#e74c3c"},
                        markers=True,
                        labels={"value": "Pontuação", "Partida": "Histórico de Jogos", "variable": "Indicador"}
                    )
                    
                    # Altera as legendas que aparecem no gráfico para ficar mais amigável
                    newnames = {col_pp: 'Pontos Pró (PP)', col_pc: 'Pontos Contra (PC)'}
                    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                    
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.info("Nenhum dado corresponde aos filtros aplicados nas caixas de pesquisa.")
