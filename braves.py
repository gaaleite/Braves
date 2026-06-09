import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")

st.title("🏈 Braves Academy- Gerenciador de Jogos")

# LINK DA SUA PLANILHA (Substitua pelo seu link de compartilhamento)
URL_NORMAL = "https://docs.google.com/spreadsheets/u/0/d/1ZOetHxxdpHmPe2aCfPvli51YxXgD0LcFIVUEFIT6sDg/htmlview?pli=1"

# -------------------------------------------------------------------------
# FUNÇÃO DE LEITURA DIRETA DO GOOGLE SHEETS VIA PANDAS
# -------------------------------------------------------------------------
@st.cache_data(ttl=10) # Atualiza automaticamente a cada 10 segundos
def carregar_aba_google(url_planilha, nome_aba):
    try:
        base_url = url_planilha.split("/edit")
        csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(csv_url)
        if not df.empty:
            # Remove apenas espaços extras das colunas, mantendo maiúsculas/minúsculas originais
            df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

# -------------------------------------------------------------------------
# GERENCIAMENTO DOS DADOS EM MEMÓRIA
# -------------------------------------------------------------------------
if "lista_abas" not in st.session_state:
    st.session_state.lista_abas = ["ALL GAMES"]

# -------------------------------------------------------------------------
# INTERFACE: ADICIONAR NOVA ABA
# -------------------------------------------------------------------------
with st.expander("➕ Adicionar Nova Aba / Categoria"):
    nova_aba_input = st.text_input("Nome da nova aba:", placeholder="Ex: playoffs 25").strip()
    if st.button("Criar Aba"):
        if nova_aba_input and nova_aba_input not in st.session_state.lista_abas:
            st.session_state.lista_abas.append(nova_aba_input)
            st.success(f"Aba '{nova_aba_input}' criada com sucesso!")
            st.rerun()

# Criação visual das abas no navegador
tabs = st.tabs(st.session_state.lista_abas)

# Carrega os dados da planilha principal
df_todos_jogos = carregar_aba_google(URL_NORMAL, "ALL GAMES")

# MAPEAMENTO DE COLUNAS (Tenta encontrar a coluna mesmo que mude maiúscula/minúscula)
def obter_coluna_real(df, nomes_possiveis):
    for nome in nomes_possiveis:
        for col in df.columns:
            if col.lower() == nome.lower():
                return col
    return None

# Mapeia dinamicamente os nomes das colunas baseado no que está na sua planilha
col_data = obter_coluna_real(df_todos_jogos, ["data", "date"]) or "DATA"
col_ano = obter_coluna_real(df_todos_jogos, ["ano", "year"]) or "ANO"
col_jogo = obter_coluna_real(df_todos_jogos, ["jogo", "game"]) or "JOGO"
col_time = obter_coluna_real(df_todos_jogos, ["time", "team"]) or "TIME"
col_cidade = obter_coluna_real(df_todos_jogos, ["cidade", "estado"]) or "CIDADE", "ESTADO"
col_vit = obter_coluna_real(df_todos_jogos, ["vitoria", "vitória", "v"]) or "V"
col_derr = obter_coluna_real(df_todos_jogos, ["derrota", "d"]) or "D"
col_emp = obter_coluna_real(df_todos_jogos, ["empate", "e"]) or "E"
col_adv = obter_coluna_real(df_todos_jogos, ["adversario", "adversário"]) or "ADVERSARIO"

colunas_finais = [col_data, col_ano, col_jogo, col_time, col_cidade, col_vit, col_derr, col_emp, col_adv]

# Garante que o DataFrame não esteja quebrado caso a planilha falhe na leitura
if df_todos_jogos.empty:
    df_todos_jogos = pd.DataFrame(columns=colunas_finais)
else:
    for col in colunas_finais:
        if col not in df_todos_jogos.columns:
            df_todos_jogos[col] = ""

# Renderizar o conteúdo de cada aba
for i, nome_da_aba in enumerate(st.session_state.lista_abas):
    with tabs[i]:
        st.subheader(f"Painel: {nome_da_aba}")
        
        if nome_da_aba == "ALL GAMES":
            st.write("### 🔍 Filtros de Pesquisa")
            st.caption("Digite nos campos abaixo para filtrar o gráfico em tempo real. Deixe em branco para ver todos os dados.")
            
            # --- ORGANIZAÇÃO DOS FILTROS DE 3 EM 3 (LINHA 1) ---
            f1, f2, f3 = st.columns(3)
            busca_data = f1.text_input("🗓 Filtrar por Data", placeholder="Ex: 12/05", key="f_data").strip()
            busca_ano = f2.text_input("📆 Filtrar por Ano", placeholder="Ex: 2025", key="f_ano").strip()
            busca_jogo = f3.text_input("🏈 Filtrar por Jogo", placeholder="Ex: Amistoso", key="f_jogo").strip()
            
            # --- ORGANIZAÇÃO DOS FILTROS DE 3 EM 3 (LINHA 2) ---
            f4, f5, f6 = st.columns(3)
            busca_time = f4.text_input("🛡️ Filtrar por Time", placeholder="Ex: Sub 14", key="f_time").strip()
            busca_cidade = f5.text_input("📍 Filtrar por Cidade-Estado", placeholder="Ex: SÃO PAULO-SP", key="f_cidade").strip()
            busca_adversario = f6.text_input("🛡️💥🛡️ Filtrar por Adversário", placeholder="Ex:Vikings", key="f_adv").strip()
            
            # --- ORGANIZAÇÃO DOS FILTROS DE 3 EM 3 (LINHA 3) ---
            f7, f8, f9 = st.columns(3)
            busca_vit = f7.text_input("🏆 Filtrar por Vitória", placeholder="Ex: V", key="f_vit").strip()
            busca_derr = f8.text_input("❌ Filtrar por Derrota", placeholder="Ex: D", key="f_derr").strip()
            busca_emp = f9.text_input("🤝 Filtrar por Empate (Qtd)", placeholder="Ex: E", key="f_emp").strip()
            
            # Aplicando os filtros dinâmicos de forma totalmente insensível a maiúsculas/minúsculas
            df_filtrado = df_todos_jogos.copy()
            
            if busca_data:
                df_filtrado = df_filtrado[df_filtrado[col_data].astype(str).str.upper().str.contains(busca_data.upper(), na=False)]
            if busca_ano:
                df_filtrado = df_filtrado[df_filtrado[col_ano].astype(str).str.upper().str.contains(busca_ano.upper(), na=False)]
            if busca_jogo:
                df_filtrado = df_filtrado[df_filtrado[col_jogo].astype(str).str.upper().str.contains(busca_jogo.upper(), na=False)]
            if busca_time:
                df_filtrado = df_filtrado[df_filtrado[col_time].astype(str).str.upper().str.contains(busca_time.upper(), na=False)]
            if busca_cidade:
                df_filtrado = df_filtrado[df_filtrado[col_cidade].astype(str).str.upper().str.contains(busca_cidade.upper(), na=False)]
            if busca_adversario:
                df_filtrado = df_filtrado[df_filtrado[col_adv].astype(str).str.upper().str.contains(busca_adversario.upper(), na=False)]
            if busca_vit:
                df_filtrado = df_filtrado[df_filtrado[col_vit].astype(str).str.upper().str.contains(busca_vit.upper(), na=False)]
            if busca_derr:
                df_filtrado = df_filtrado[df_filtrado[col_derr].astype(str).str.upper().str.contains(busca_derr.upper(), na=False)]
            if busca_emp:
                df_filtrado = df_filtrado[df_filtrado[col_emp].astype(str).str.upper().str.contains(busca_emp.upper(), na=False)]
                
            st.markdown("---")
            st.write("### 📈 Gráfico de Desempenho")
            
            if not df_filtrado.empty:
                df_filtrado = df_filtrado.reset_index(drop=True)
                
                # Monta a legenda do Eixo Y usando os nomes mapeados das colunas
                df_filtrado["Eixo_Esquerdo"] = (
                    df_filtrado[col_data].astype(str) + " | " +
                    df_filtrado[col_ano].astype(str) + " | " +
                    df_filtrado[col_jogo].astype(str) + " | " +
                    df_filtrado[col_time].astype(str) + " | " +
                    df_filtrado[col_cidade].astype(str) + " vs " +
                    df_filtrado[col_adv].astype(str)
                )
                
                colunas_resultado = [col_vit, col_derr, col_emp]
                for col in colunas_resultado:
                    df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)
                
                # Renderiza o gráfico de barras horizontais
                fig = px.bar(
                    df_filtrado,
                    y="Eixo_Esquerdo",
                    x=colunas_resultado,
                    barmode="group",
                    labels={"value": "Quantidade", "Eixo_Esquerdo": "Informações do Jogo", "variable": "Resultado"},
                    orientation="h",
                    color_discrete_map={col_vit: "#2ECC71", col_derr: "#E74C3C", col_emp: "#F1C40F"}
                )
                
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400 + (len(df_filtrado) * 30))
                st.plotly_chart(fig, use_container_width=True)
                
                st.write("#### 📋 Dados Filtrados")
                st.dataframe(df_filtrado[colunas_finais], use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum dado encontrado com os filtros aplicados ou a planilha está vazia.")
        else:
            st.info(f"Aba personalizada criada para armazenar informações futuras sobre: {nome_da_aba}")
