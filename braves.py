import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# =========================================================================
# CONFIGURAÇÃO DOS LINKS - INSIRA OS SEUS LINKS AQUI
# =========================================================================
# Link de leitura (deve terminar com /export?format=csv para o pandas ler direto)
URL_LEITURA_CSV = "https://google.com"

# Link do Google Apps Script gerado no Passo 1
URL_GRAVACAO_SCRIPT = "https://google.com"
# =========================================================================

@st.cache_data(ttl=5)
def carregar_dados_posicionais(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        if not df.empty:
            qtd_colunas = len(df.columns)
            df_limpo = pd.DataFrame()
            
            # Mapeamento exato por índices físicos do seu ecossistema
            if qtd_colunas >= 2:   df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()
            if qtd_colunas >= 3:   df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()
            if qtd_colunas >= 4:   df_limpo["JOGO"] = df.iloc[:, 3].astype(str).str.strip()
            if qtd_colunas >= 5:   df_limpo["TIME"] = df.iloc[:, 4].astype(str).str.strip()
            if qtd_colunas >= 7:   df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()
            if qtd_colunas >= 8:   df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()
            if qtd_colunas >= 9:   df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip()
            
            if qtd_colunas >= 11:  df_limpo["PP"] = pd.to_numeric(df.iloc[:, 10], errors='coerce').fillna(0)
            if qtd_colunas >= 12:  df_limpo["PC"] = pd.to_numeric(df.iloc[:, 11], errors='coerce').fillna(0)
            if qtd_colunas >= 13:  df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()
            
            # Limpezas nativas anti-ruído
            df_limpo = df_limpo[~df_limpo["JOGO"].str.contains(r"\{|function|var|index|void|call|html", case=False, na=True)]
            df_limpo = df_limpo[df_limpo["JOGO"] != "nan"]
            df_limpo = df_limpo[df_limpo["JOGO"] != ""]
            
            return df_limpo.reset_index(drop=True)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_jogos = carregar_dados_posicionais(URL_LEITURA_CSV)

# Criação das Abas Estáveis
aba_graficos, aba_adicionar = st.tabs(["📊 Gráfico de Jogos", "➕ Adicionar Novo Jogo"])

# ==========================================
# ABA 1: GRÁFICOS E FILTROS
# ==========================================
with aba_graficos:
    if not df_jogos.empty:
        st.write("### 🔍 Filtros de Pesquisa")
        
        f1, f2 = st.columns(2)
        busca_data = f1.text_input("🗓 Data", placeholder="Ex: 12/05", key="f_data").strip()
        busca_ano = f2.text_input("📆 Ano", placeholder="Ex: 2025", key="f_ano").strip()
        
        f3, f4, f5 = st.columns(3)
        busca_time = f3.text_input("🛡️ Categoria / Time", placeholder="Ex: Sub 14", key="f_time").strip()
        busca_cidade = f4.text_input("📍 Cidade", placeholder="Ex: São Paulo", key="f_cidade").strip()
        busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: Fox", key="f_adv").strip()
        
        f6_col, = st.columns(1)
        busca_vd = f6_col.text_input("🏆 Resultados (V / D / E)", placeholder="Ex: V", key="f_vd").strip()
        
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
        
        if not df_filtrado.empty:
            df_filtrado = df_filtrado.reset_index(drop=True)
            st.write("### 📈 Linha de Tendência e Pontuação")
            
            df_filtrado["Partida"] = "J" + df_filtrado["JOGO"] + " - " + df_filtrado["TIME"] + " vs " + df_filtrado["ADVERSARIO"]
            
            fig = px.line(
                df_filtrado,
                x="Partida",
                y=["PP", "PC"],
                title="Evolução de Pontos Feitos (PP) vs Pontos Sofridos (PC)",
                color_discrete_map={"PP": "#2ecc71", "PC": "#e74c3c"},
                markers=True,
                labels={"value": "Pontuação", "Partida": "Histórico de Jogos", "variable": "Indicador"}
            )
            newnames = {'PP': 'Pontos Pró (PP)', 'PC': 'Pontos Contra (PC)'}
            fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado corresponde aos filtros aplicados.")
    else:
        st.warning("Verifique o link da sua planilha ou aguarde o carregamento.")

# ==========================================
# ABA 2: FORMULÁRIO (GRAVAÇÃO INTERNA VIA API)
# ==========================================
with aba_adicionar:
    st.write("### 📝 Cadastrar Nova Partida")
    st.caption("Insira os dados para salvar diretamente no Google Sheets de forma instantânea.")
    
    with st.form(key="form_cadastro_nativo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        input_data = c1.text_input("🗓 Data do Jogo", placeholder="Ex: 12/05")
        input_ano = c2.text_input("📆 Ano", placeholder="Ex: 2026")
        input_jogo = c3.text_input("🔢 Número do Jogo (ID)", placeholder="Ex: 42")
        
        c4, c5, c6 = st.columns(3)
        input_time = c4.text_input("🛡️ Categoria / Nosso Time", placeholder="Ex: Sub 14")
        input_adversario = c5.text_input("⚔️ Adversário", placeholder="Ex: Fox")
        input_vd = c6.selectbox("🏆 Resultado", ["V", "D", "E"])
        
        c7, c8 = st.columns(2)
        input_cidade = c7.text_input("📍 Cidade", placeholder="Ex: Sorocaba")
        input_estado = c8.text_input("🏳️ Estado (UF)", placeholder="Ex: SP", max_chars=2)
        
        c9, c10 = st.columns(2)
        input_pp = c9.number_input("🟢 Pontos Pró (PP)", min_value=0, step=1, value=0)
        input_pc = c10.number_input("🔴 Pontos Contra (PC)", min_value=0, step=1, value=0)
        
        botao_enviar = st.form_submit_button("💾 Salvar no Google Sheets")
        
        if botao_enviar:
            if not input_jogo or not input_time or not input_adversario:
                st.error("⚠️ Os campos 'Número do Jogo', 'Time' e 'Adversário' são obrigatórios!")
            else:
                # Prepara o payload estruturado para o Apps Script
                payload = {
                    "data": input_data,
                    "ano": input_ano,
                    "jogo": input_jogo,
                    "time": input_time,
                    "cidade": input_cidade,
                    "estado": input_estado,
                    "vd": input_vd,
                    "pp": int(input_pp),
                    "pc": int(input_pc),
                    "adversario": input_adversario
                }
                
                try:
                    with st.spinner("Enviando dados para a nuvem..."):
                        resposta = requests.post(URL_GRAVACAO_SCRIPT, data=json.dumps(payload))
                    
                    if resposta.status_code == 200:
                        st.success("✅ Partida adicionada com sucesso no Google Sheets!")
                        st.cache_data.clear() # Reseta o cache para puxar o jogo recém-salvo no gráfico
                    else:
                        st.error(f"Erro no servidor Google (Status {resposta.status_code}). Verifique a implantação do Script.")
                except Exception as erro_req:
                    st.error(f"Falha de comunicação: {erro_req}")
