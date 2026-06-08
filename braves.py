import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")

st.title("🏈 Braves - Gerenciador de Jogos (Google Sheets)")

# LINK DA SUA PLANILHA DO GOOGLE DRIVE
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1ZOetHxxdpHmPe2aCfPvli51YxXgD0LcFIVUEFIT6sDg/edit?usp=drive_link"

# Inicializa a conexão nativa do Streamlit com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# -------------------------------------------------------------------------
# FUNÇÕES DE LEITURA E ESCRITA (PANDAS + GOOGLE SHEETS)
# -------------------------------------------------------------------------
@st.cache_data(ttl=5) # Atualiza os dados a cada 5 segundos se houver mudanças
def ler_dados(aba_nome):
    try:
        return conn.read(spreadsheet=URL_PLANILHA, worksheet=aba_nome)
    except Exception:
        return pd.DataFrame()

def salvar_dados(df, aba_nome):
    conn.update(spreadsheet=URL_PLANILHA, worksheet=aba_nome, data=df)
    st.cache_data.clear()

# Carrega a configuração das abas do sistema
df_abas_config = ler_dados("abas_config")

# Se a planilha estiver vazia, cria a estrutura inicial padrão
if df_abas_config.empty or "nome_aba" not in df_abas_config.columns:
    df_abas_config = pd.DataFrame({"nome_aba": ["todos os jogos", "classificações", "houston 25"]})
    salvar_dados(df_abas_config, "abas_config")

lista_abas = df_abas_config["nome_aba"].dropna().tolist()

# -------------------------------------------------------------------------
# INTERFACE INTERATIVA
# -------------------------------------------------------------------------

# Seção para adicionar novas abas (Botão "+")
with st.expander("➕ Adicionar Nova Aba / Categoria"):
    nova_aba_input = st.text_input("Nome da nova aba:", placeholder="Ex: playoffs 25").strip().lower()
    if st.button("Criar Aba"):
        if nova_aba_input and nova_aba_input not in lista_abas:
            nova_linha = pd.DataFrame({"nome_aba": [nova_aba_input]})
            df_abas_config = pd.concat([df_abas_config, nova_linha], ignore_index=True)
            salvar_dados(df_abas_config, "abas_config")
            st.success(f"Aba '{nova_aba_input}' criada com sucesso!")
            st. those_rows = st.rerun()

# Criação visual das abas no navegador
tabs = st.tabs([aba.title() for aba in lista_abas])

# Carregar tabelas globais para filtrar por aba
df_jogos_geral = ler_dados("dados_jogos")
df_comissao_geral = ler_dados("comissao_tecnica")
df_atletas_geral = ler_dados("atletas")

# Garantir colunas mínimas caso estejam vazias
if df_jogos_geral.empty:
    df_jogos_geral = pd.DataFrame(columns=["aba", "ano", "dia", "torneio", "td", "conversao", "safety", "interceptacao"])
if df_comissao_geral.empty:
    df_comissao_geral = pd.DataFrame(columns=["aba", "nome", "funcao"])
if df_atletas_geral.empty:
    df_atletas_geral = pd.DataFrame(columns=["aba", "nome", "posicao"])

# Renderizar o conteúdo de cada aba
for i, nome_da_aba in enumerate(lista_abas):
    with tabs[i]:
        st.subheader(f"Painel: {nome_da_aba.title()}")
        
        # 📊 SEÇÃO DO GRÁFICO DINÂMICO
        st.write("### 📈 Gráfico de Desempenho")
        
        # Filtrar dados desta aba específica
        df_jogos_aba = df_jogos_geral[df_jogos_geral["aba"] == nome_da_aba]
        
        if not df_jogos_aba.empty:
            # Junta as colunas no canto esquerdo (Eixo Y)
            df_jogos_aba["Eixo_Esquerdo"] = (
                df_jogos_aba["ano"].astype(str) + " | " + 
                df_jogos_aba["dia"].astype(str) + " | " + 
                df_jogos_aba["torneio"].astype(str)
            )
            
            # Gera o gráfico com as métricas na parte inferior (Eixo X)
            fig = px.bar(
                df_jogos_aba,
                y="Eixo_Esquerdo",
                x=["td", "conversao", "safety", "interceptacao"],
                barmode="group",
                labels={"value": "Quantidade", "Eixo_Esquerdo": "Ano | Dia | Torneio", "variable": "Estatística"},
                orientation="h"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insira dados de jogos abaixo para gerar o gráfico.")

        # Formulário rápido para inserir dados do gráfico (Jogos)
        with st.expander("➕ Adicionar Novo Jogo / Dados do Gráfico"):
            c1, c2, c3 = st.columns(3)
            ano = c1.text_input("Ano", key=f"ano_{nome_da_aba}")
            dia = c2.text_input("Dia (dd/mm)", key=f"dia_{nome_da_aba}")
            torneio = c3.text_input("Torneio", key=f"tor_{nome_da_aba}")
            
            c4, c5, c6, c7 = st.columns(4)
            td = c4.number_input("TD", min_value=0, step=1, key=f"td_{nome_da_aba}")
            conv = c5.number_input("Conversão", min_value=0, step=1, key=f"cv_{nome_da_aba}")
            saf = c6.number_input("Safety", min_value=0, step=1, key=f"sf_{nome_da_aba}")
            inter = c7.number_input("Interceptação", min_value=0, step=1, key=f"int_{nome_da_aba}")
            
            if st.button("Salvar Jogo", key=f"btn_jogo_{nome_da_aba}"):
                novo_jogo = pd.DataFrame([{
                    "aba": nome_da_aba, "ano": ano, "dia": dia, "torneio": torneio,
                    "td": td, "conversao": conv, "safety": saf, "interceptacao": inter
                }])
                df_jogos_geral = pd.concat([df_jogos_geral, novo_jogo], ignore_index=True)
                salvar_dados(df_jogos_geral, "dados_jogos")
                st.success("Jogo adicionado!")
                st.rerun()

        st.markdown("---")
        
        # 🏢 SEÇÃO DAS TABELAS LADO A LADO
        col1, espaco, col2 = st.columns([1, 0.1, 1])
        
        with col1:
            st.write("### 📋 Comissão Técnica")
            df_com_aba = df_comissao_geral[df_comissao_geral["aba"] == nome_da_aba][["nome", "funcao"]].reset_index(drop=True)
            
            # Tabela editável dinâmica (O botão "+" aparece no rodapé dela automaticamente)
            df_com_editada = st.data_editor(df_com_aba, num_rows="dynamic", key=f"edt_com_{nome_da_aba}", use_container_width=True)
            
            if st.button("Salvar Comissão", key=f"sv_com_{nome_da_aba}"):
                df_com_editada["aba"] = nome_da_aba
                # Remove dados antigos dessa aba e salva os novos
                df_restante = df_comissao_geral[df_comissao_geral["aba"] != nome_da_aba]
                df_final = pd.concat([df_restante, df_com_editada], ignore_index=True)
                salvar_dados(df_final, "comissao_tecnica")
                st.success("Comissão atualizada!")
                st.rerun()

        with col2:
            st.write("### 🏃 Atletas")
            df_atl_aba = df_atletas_geral[df_atletas_geral["aba"] == nome_da_aba][["nome", "posicao"]].reset_index(drop=True)
            
            # Tabela editável dinâmica
            df_atl_editada = st.data_editor(df_atl_aba, num_rows="dynamic", key=f"edt_atl_{nome_da_aba}", use_container_width=True)
            
            if st.button("Salvar Atletas", key=f"sv_atl_{nome_da_aba}"):
                df_atl_editada["aba"] = nome_da_aba
                # Remove dados antigos dessa aba e salva os novos
                df_restante = df_atletas_geral[df_atletas_geral["aba"] != nome_da_aba]
                df_final = pd.concat([df_restante, df_atl_editada], ignore_index=True)
                salvar_dados(df_final, "atletas")
                st.success("Atletas atualizados!")
                st.rerun()
