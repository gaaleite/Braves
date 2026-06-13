import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.request
import io

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# Injeta CSS para aplicar o fundo azul-marinho profundo e ajustar os filtros
css_fundo_azul_marinho = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0a192f; /* Azul-marinho profundo e profissional */
}

/* Força títulos e subtextos principais a ficarem brancos */
h1, h2, h3, p, span, label, [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}

/* 1. Altera fundo de caixas de texto (inputs) e seletores (selectbox) para branco */
input, select, div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* 2. Força todas as letras internas do selectbox ativo e do placeholder ficarem pretas */
div[data-baseweb="select"] *, input::placeholder {
    color: #000000 !important;
}

/* 3. Ajusta o fundo e texto do menu dropdown (quando clicado) para não herdar o tema escuro */
div[role="listbox"] ul {
    background-color: #ffffff !important;
}
div[role="listbox"] li {
    color: #000000 !important;
}

/* 4. Altera o comportamento visual ao passar o mouse por cima das opções da lista */
div[role="listbox"] li:hover {
    background-color: #f0f2f6 !important;
    color: #000000 !important;
}
</style>
"""
st.markdown(css_fundo_azul_marinho, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        # Link oficial fornecido
        url_original = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNg8QGIcR3oocTpka0agajCb-CF37OWvuJuG66FeMrhgAOY6qpg8zlej9iGK7dTQ1jQX8Gc_VahDPo/pubhtml?gid=516798055&single=true"
        
        url_csv = url_original.replace("/pubhtml", "/pub")
        if "&output=csv" not in url_csv:
            url_csv += "&output=csv"
        
        req = urllib.request.Request(url_csv, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            dados_brutos = response.read()
            
        df = pd.read_csv(io.BytesIO(dados_brutos), header=None, on_bad_lines="skip")
        
        if df.empty:
            return pd.DataFrame()

        qtd_colunas = len(df.columns)
        df_limpo = pd.DataFrame()

        if qtd_colunas >= 1:
            df_limpo["JOGO"] = df.iloc[:, 0].astype(str).str.strip()
        if qtd_colunas >= 2:
            df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()
        if qtd_colunas >= 3:
            df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()
        if qtd_colunas >= 4:
            df_limpo["TORNEIO"] = df.iloc[:, 3].astype(str).str.strip()
        if qtd_colunas >= 5:
            df_limpo["FAIXA_ETARIA"] = df.iloc[:, 4].astype(str).str.strip()
        if qtd_colunas >= 6:
            df_limpo["CATEGORIA"] = df.iloc[:, 5].astype(str).str.strip()
        if qtd_colunas >= 7:
            df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()
        if qtd_colunas >= 8:
            df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()
        if qtd_colunas >= 9:
            df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip()
        
        pp_raw = df.iloc[:, 10].astype(str).str.strip() if qtd_colunas >= 11 else "0"
        pc_raw = df.iloc[:, 11].astype(str).str.strip() if qtd_colunas >= 12 else "0"
        
        if qtd_colunas >= 13:
            df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()
        else:
            df_limpo["ADVERSARIO"] = "Desconhecido"

        df_limpo = df_limpo[df_limpo["JOGO"].str.isnumeric()]

        df_limpo["PP"] = pd.to_numeric(pp_raw.loc[df_limpo.index], errors="coerce").fillna(0).astype(int)
        df_limpo["PC"] = pd.to_numeric(pc_raw.loc[df_limpo.index], errors="coerce").fillna(0).astype(int)

        return df_limpo.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao processar dados da tabela: {e}")
        return pd.DataFrame()

df_jogos = carregar_dados()

if df_jogos.empty:
    st.error("⚠️ O banco de dados retornou vazio. Verifique se o link foi publicado corretamente no menu do Drive.")
else:
    st.write("### 🔍 Filtros de Pesquisa")

    f1, f2, f3 = st.columns(3)
    busca_data = f1.text_input("🗓️ Data", placeholder="Ex: 07/06").strip()
    busca_ano = f2.text_input("📅 Ano", placeholder="Ex: 2026").strip()
    
    opcoes_time = ["Todos"] + sorted(list(df_jogos["FAIXA_ETARIA"].unique()))
    busca_time_categoria = f3.selectbox("🛡️ Time (Categoria)", opcoes_time)

    f4, f5, f6 = st.columns(3)
    busca_cidade = f4.text_input("🗺️ Cidade", placeholder="Ex: São Paulo").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: 4Fun").strip()
    busca_vd = f6.text_input("🎖️ Resultados (V / D / E)", placeholder="Ex: V").strip()

    df_filtrado = df_jogos.copy()

    if busca_data:
        df_filtrado = df_filtrado[df_filtrado["DATA"].str.contains(busca_data, na=False)]
    if busca_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO"].str.contains(busca_ano, na=False)]
    if busca_time_categoria != "Todos":
        df_filtrado = df_filtrado[df_filtrado["FAIXA_ETARIA"] == busca_time_categoria]
    if busca_cidade:
        df_filtrado = df_filtrado[df_filtrado["CIDADE"].str.upper().str.contains(busca_cidade.upper(), na=False)]
    if busca_adversario:
        df_filtrado = df_filtrado[df_filtrado["ADVERSARIO"].str.upper().str.contains(busca_adversario.upper(), na=False)]
    if busca_vd:
        df_filtrado = df_filtrado[df_filtrado["VD"].str.upper().str.contains(busca_vd.upper(), na=False)]

    st.markdown("---")

    if not df_filtrado.empty:
        df_filtrado = df_filtrado.reset_index(drop=True)

        st.write("### 📊 Indicadores Gerais")
        m1, m2, m3 = st.columns(3)

        total_jogos = len(df_filtrado)
        total_pp = int(df_filtrado["PP"].sum())
        total_pc = int(df_filtrado["PC"].sum())

        m1.metric("Total de Partidas", total_jogos, f"De {len(df_jogos)} registradas")
        m2.metric("Pontos Pró Acumulados (PP)", total_pp, "Pontos Feitos")
        m3.metric("Pontos Contra Acumulados (PC)", total_pc, "- Pontos Sofridos", delta_color="inverse")

        st.markdown("---")
        st.write("### 📈 Histórico Dinâmico de Atividade")

        # Organiza os dados cronologicamente
        df_grafico = df_filtrado.copy()
        df_grafico["ID_NUM"] = pd.to_numeric(df_grafico["JOGO"], errors="coerce")
        df_grafico = df_grafico.sort_values(by="ID_NUM", ascending=True)

        df_grafico["Rotulo_EixoX"] = "Jogo " + df_grafico["JOGO"]
        df_grafico["Texto_Coluna"] = "<b>" + df_grafico["PP"].astype(str) + "x" + df_grafico["PC"].astype(str) + "</b><br><span style='font-size:9px; opacity:0.8;'>" + df_grafico["DATA"] + "</span>"
        df_grafico["Texto_Hover"] = "<b>Jogo " + df_grafico["JOGO"] + "</b><br>📅 Data: " + df_grafico["DATA"] + " / " + df_grafico["ANO"] + "<br>🛡️ Categoria: " + df_grafico["FAIXA_ETARIA"] + "<br>⚔️ Adversário: " + df_grafico["ADVERSARIO"] + "<br>🏆 Placar: " + df_grafico["PP"].astype(str) + " x " + df_grafico["PC"].astype(str)

        cores_barras = []
        for pp, pc in zip(df_grafico["PP"], df_grafico["PC"]):
            if pp > pc:
                cores_barras.append("#00b4d8")
            elif pp < pc:
                cores_barras.append("#ef476f")
            else:
                cores_barras.append("#ffd166")

        # --- CONTROLE DE JANELA USANDO BOTÕES NATIVOS DO STREAMLIT ---
        total_jogos_atuais = len(df_grafico)
        
        # Cria os botões lado a lado para o usuário escolher o foco com segurança
        col_btn1, col_btn2 = st.columns(2)
        
        # Inicializa o estado de visualização
        if "modo_janela" not in st.session_state:
            st.session_state["modo_janela"] = "recentes"

        if col_btn1.button("⬅️ Focar nos Jogos Mais Antigos", use_container_width=True):
            st.session_state["modo_janela"] = "antigos"
            
        if col_btn2.button("Focar nos Jogos Mais Recentes ➡️", use_container_width=True):
            st.session_state["modo_janela"] = "recentes"

        # Define os limites do eixo X com base na escolha do botão
        if st.session_state["modo_janela"] == "antigos":
            range_atual = [-0.5, 14.5]
        else:
            indice_inicial = max(0, total_jogos_atuais - 15)
            range_atual = [indice_inicial - 0.5, total_jogos_atuais - 0.5]

        # Montagem limpa da figura Plotly
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_grafico["Rotulo_EixoX"],
            y=df_grafico["PP"],
            name="Pontos Pró",
            marker_color=cores_barras,
            text=df_grafico["Texto_Coluna"],
            textposition="auto",
            hoverinfo="text",
            hovertext=df_grafico["Texto_Hover"]
        ))

        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            height=450,
            margin=dict(l=10, r=10, t=10, b=10)
        )

        fig.update_xaxes(
            type="category",
            range=range_atual,
            rangeslider=dict(visible=True, thickness=0.08)  # Mantém a barra de arrastar por toque ativa
        )

        fig.update_yaxes(title_text="Pontos")

        # Renderização do gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # --- EXIBIÇÃO DA TABELA DE REGISTROS LOGO ABAIXO ---
        st.markdown("---")
        st.write("### 📋 Tabela de Registros Filtrados")
        st.dataframe(df_filtrado, use_container_width=True)
        
    else:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
