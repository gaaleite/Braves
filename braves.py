import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.request
import io

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# Injeta CSS para aplicar o fundo azul-marinho profundo e ajustar os filtros
css_fundo_azul_marinho = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0a192f;
}
h1, h2, h3, p, span, label, [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}
input, select, div[data-baseweb="select"] > div, div[data-baseweb="tag"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
div[data-baseweb="select"] *, input::placeholder, div[data-baseweb="tag"] span {
    color: #000000 !important;
}
div[data-baseweb="tag"] role[button], div[data-baseweb="tag"] svg {
    fill: #000000 !important;
}
div[role="listbox"] ul {
    background-color: #ffffff !important;
}
div[role="listbox"] li {
    color: #000000 !important;
}
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
    st.error("⚠️ O banco de dados retornou vazio. Verifique a publicação no Drive.")
else:
    st.write("### 🔍 Filtros de Pesquisa")

    f1, f2, f3 = st.columns(3)
    busca_data = f1.text_input("🗓️ Data", placeholder="Ex: 07/06").strip()
    
    opcoes_anos = sorted(list(df_jogos["ANO"].unique()), reverse=True)
    busca_anos = f2.multiselect("📅 Anos (Selecione 1 ou mais)", opcoes_anos, placeholder="Ex: Escolha os anos")
    
    opcoes_time = ["Todos"] + sorted(list(df_jogos["FAIXA_ETARIA"].unique()))
    busca_time_categoria = f3.selectbox("🛡️ Time (Categoria)", opcoes_time)

    f4, f5, f6 = st.columns(3)
    busca_cidade = f4.text_input("🗺️ Cidade", placeholder="Ex: São Paulo").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: 4Fun").strip()
    busca_vd = f6.text_input("🎖️ Resultados (V / D / E)", placeholder="Ex: V").strip()

    df_filtrado = df_jogos.copy()

    if busca_data:
        df_filtrado = df_filtrado[df_filtrado["DATA"].str.contains(busca_data, na=False)]
    if busca_anos:
        df_filtrado = df_filtrado[df_filtrado["ANO"].isin(busca_anos)]
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

        df_grafico = df_filtrado.copy()
        df_grafico["ID_NUM"] = pd.to_numeric(df_grafico["JOGO"], errors="coerce")
        df_grafico = df_grafico.sort_values(by="ID_NUM", ascending=True)

        # Rótulo padrão limpo e legível
        df_grafico["Rotulo_EixoX"] = "J" + df_grafico["JOGO"] + " (" + df_grafico["ANO"] + ")"
        df_grafico["Texto_Coluna"] = df_grafico["PP"].astype(str) + "x" + df_grafico["PC"].astype(str)
        df_grafico["Texto_Hover"] = "Jogo " + df_grafico["JOGO"] + "<br>Data: " + df_grafico["DATA"] + "<br>Adversário: " + df_grafico["ADVERSARIO"]

        # Define as cores originais das barras por Resultado (Vitória = Verde)
        cores_barras = []
        for pp, pc in zip(df_grafico["PP"], df_grafico["PC"]):
            if pp > pc:
                cores_barras.append("#00c49f")
            elif pp < pc:
                cores_barras.append("#ef476f")
            else:
                cores_barras.append("#ffd166")

        total_jogos_atuais = len(df_grafico)
        col_btn1, col_btn2 = st.columns(2)
        
        if "modo_janela" not in st.session_state:
            st.session_state["modo_janela"] = "recentes"

        if col_btn1.button("⬅️ Focar nos Jogos Mais Antigos", use_container_width=True):
            st.session_state["modo_janela"] = "antigos"
        if col_btn2.button("Focar nos Jogos Mais Recentes ➡️", use_container_width=True):
            st.session_state["modo_janela"] = "recentes"

        if st.session_state["modo_janela"] == "antigos":
            range_atual = [-0.5, 14.5]
        else:
            indice_inicial = max(0, total_jogos_atuais - 15)
            range_atual = [indice_inicial - 0.5, total_jogos_atuais - 0.5]

        fig = px.bar(
            df_grafico,
            x="Rotulo_EixoX",
            y="PP",
            text="Texto_Coluna",
            custom_data=["Texto_Hover"]
        )

        fig.update_traces(
            marker_color=cores_barras,
            textposition="auto",
            hovertemplate="%{customdata}<extra></extra>"
        )

        fig.update_layout(
            template="plotly_dark",
            height=450,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                type="category",
                range=range_atual,
                title_text="Anos",
                rangeslider=dict(visible=True, thickness=0.08)
            ),
            yaxis=dict(title="Pontos")
        )

        # --- LÓGICA AUTOMÁTICA DE LINHAS DIVISÓRIAS POR MUDANÇA DE ANO ---
        # Varre os jogos procurando o ponto exato onde o ano muda para traçar a linha divisória
        ultimo_ano = None
        for i, ano_atual in enumerate(df_grafico["ANO"]):
            if ultimo_ano is not None and ano_atual != ultimo_ano:
                # Desenha uma linha vertical tracejada branca entre os anos diferentes
                fig.add_vline(
                    x=i - 0.5, 
                    line_width=1.5, 
                    line_dash="dash", 
                    line_color="#ffffff",
                    opacity=0.6
                )
            ultimo_ano = ano_atual

        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.write("### 📋 Tabela de Registros Filtrados")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
