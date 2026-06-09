import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")

st.title("🏈 Braves - Gerenciador de Jogos (Google Sheets)")

# LINK DA SUA PLANILHA (Substitua pelo seu link de compartilhamento)
URL_NORMAL = "https://docs.google.com/spreadsheets/d/1ZOetHxxdpHmPe2aCfPvli51YxXgD0LcFIVUEFIT6sDg/edit?usp=drive_link"

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
            df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception:
        return pd.DataFrame()

# -------------------------------------------------------------------------
# GERENCIAMENTO DAS ABAS NA MEMÓRIA
# -------------------------------------------------------------------------
if "lista_abas" not in st.session_state:
    # Começa obrigatoriamente com a aba que você solicitou
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

# Mapeamento de colunas esperadas para o filtro (garante que o código não quebre se faltar na planilha)
colunas_obrigatorias = ["data", "ano", "jogo", "time", "cidade-estado", "vitoria", "derrota", "empate", "adversario"]
if df_todos_jogos.empty:
    df_todos_jogos = pd.DataFrame(columns=colunas_obrigatorias)
else:
    # Garante que todas as colunas necessárias existam no DataFrame
    for col in colunas_obrigatorias:
        if col not in df_todos_jogos.columns:
            df_todos_jogos[col] = ""

# Renderizar o conteúdo de cada aba
for i, nome_da_aba in enumerate(st.session_state.lista_abas):
    with tabs[i]:
        st.subheader(f"Painel: {nome_da_aba}")
        
        # Se for a aba principal, renderiza os gráficos e filtros de jogos
        if nome_da_aba == "ALL GAMES":
            st.write("### 🔍 Filtros de Pesquisa")
            st.caption("Digite nos campos abaixo para filtrar o gráfico em tempo real. Deixe em branco para ver todos os dados.")
            
            # Criando as caixas de texto para pesquisa (3 colunas de filtros para organizar a tela)
            f1, f2, f3 = st.columns(3)
            busca_data = f1.text_input("📅 Filtrar por Data", placeholder="Ex: 12/05", key="f_data")
            busca_ano = f2.text_input("📆 Filtrar por Ano", placeholder="Ex: 2025", key="f_ano")
            busca_jogo = f3.text_input("🎮 Filtrar por Jogo", placeholder="Ex: Jogo 1", key="f_jogo")
            
            f4, f5, f6 = st.columns(3)
            busca_time = f4.text_input("🛡️ Filtrar por Time", placeholder="Ex: Braves", key="f_time")
            busca_cidade = f5.text_input("📍 Filtrar por Cidade-Estado", placeholder="Ex: São Paulo-SP", key="f_cidade")
            busca_adversario = f6.text_input("👹 Filtrar por Adversário", placeholder="Ex: Eagles", key="f_adv")
            
            f7, f8, f9 = st.columns(3)
            busca_vit = f7.text_input("🏆 Filtrar por Vitória (Qtd)", placeholder="Ex: 1", key="f_vit")
            busca_derr = f8.text_input("❌ Filtrar por Derrota (Qtd)", placeholder="Ex: 0", key="f_derr")
            busca_emp = f9.text_input("🤝 Filtrar por Empate (Qtd)", placeholder="Ex: 0", key="f_emp")
            
            # Aplicando os filtros dinâmicos no DataFrame Pandas (ignora maiúsculas/minúsculas)
            df_filtrado = df_todos_jogos.copy()
            
            if busca_data:
                df_filtrado = df_filtrado[df_filtrado["data"].astype(str).str.contains(busca_data, case=False, na=False)]
            if busca_ano:
                df_filtrado = df_filtrado[df_filtrado["ano"].astype(str).str.contains(busca_ano, case=False, na=False)]
            if busca_jogo:
                df_filtrado = df_filtrado[df_filtrado["jogo"].astype(str).str.contains(busca_jogo, case=False, na=False)]
            if busca_time:
                df_filtrado = df_filtrado[df_filtrado["time"].astype(str).str.contains(busca_time, case=False, na=False)]
            if busca_cidade:
                df_filtrado = df_filtrado[df_filtrado["cidade-estado"].astype(str).str.contains(busca_cidade, case=False, na=False)]
            if busca_adversario:
                df_filtrado = df_filtrado[df_filtrado["adversario"].astype(str).str.contains(busca_adversario, case=False, na=False)]
            if busca_vit:
                df_filtrado = df_filtrado[df_filtrado["vitoria"].astype(str).str.contains(busca_vit, case=False, na=False)]
            if busca_derr:
                df_filtrado = df_filtrado[df_filtrado["derrota"].astype(str).str.contains(busca_derr, case=False, na=False)]
            if busca_emp:
                df_filtrado = df_filtrado[df_filtrado["empate"].astype(str).str.contains(busca_emp, case=False, na=False)]
                
            st.markdown("---")
            st.write("### 📈 Gráfico de Desempenho")
            
            if not df_filtrado.empty:
                # Cria a legenda textual informativa para o canto esquerdo do gráfico (Eixo Y)
                df_filtrado["Eixo_Esquerdo"] = (
                    df_filtrado["data"].astype(str) + " | " +
                    df_filtrado["ano"].astype(str) + " | " +
                    df_filtrado["jogo"].astype(str) + " | " +
                    df_filtrado["time"].astype(str) + " | " +
                    df_filtrado["cidade-estado"].astype(str) + " vs " +
                    df_filtrado["adversario"].astype(str)
                )
                
                # Garante que as colunas numéricas de placar/resultado sejam convertidas corretamente para a parte inferior (Eixo X)
                colunas_resultado = ["vitoria", "derrota", "empate"]
                for col in colunas_resultado:
                    df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)
                
                # Renderiza o gráfico de barras horizontais interativo
                fig = px.bar(
                    df_filtrado,
                    y="Eixo_Esquerdo",
                    x=colunas_resultado,
                    barmode="group",
                    labels={"value": "Quantidade", "Eixo_Esquerdo": "Informações do Jogo", "variable": "Resultado"},
                    orientation="h",
                    color_discrete_map={"vitoria": "#2ECC71", "derrota": "#E74C3C", "empate": "#F1C40F"} # Cores: Verde, Vermelho e Amarelo
                )
                
                # Ajuste visual para melhor leitura
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400 + (len(df_filtrado) * 30))
                st.plotly_chart(fig, use_container_width=True)
                
                # Exibe também uma tabela limpa com os dados logo abaixo para conferência rápida
                st.write("#### 📋 Dados Filtrados")
                st.dataframe(df_filtrado[colunas_obrigatorias], use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum dado encontrado com os filtros aplicados ou a planilha está vazia.")
                
        else:
            # Conteúdo genérico para as novas abas que forem criadas dinamicamente
            st.info(f"Aba personalizada criada para armazenar informações futuras sobre: {nome_da_aba}")
