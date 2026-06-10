import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        df = pd.read_csv("AllGames.csv", header=None, on_bad_lines="skip")

        if df.empty:
            return pd.DataFrame()

        qtd_colunas = len(df.columns)
        df_limpo = pd.DataFrame()

        if qtd_colunas >= 1:
            df_limpo["ID_JOGO"] = df.iloc[:, 0].astype(str).str.strip()

        if qtd_colunas >= 2:
            df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()

        if qtd_colunas >= 3:
            df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()

        if qtd_colunas >= 4:
            df_limpo["TORNEIO"] = df.iloc[:, 3].astype(str).str.strip()

        if qtd_colunas >= 5:
            df_limpo["CATEGORIA"] = df.iloc[:, 4].astype(str).str.strip()

        if qtd_colunas >= 7:
            df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()

        if qtd_colunas >= 8:
            df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()

        if qtd_colunas >= 9:
            df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip()

        if qtd_colunas >= 11:
            df_limpo["PP_RAW"] = df.iloc[:, 10].astype(str).str.strip()

        if qtd_colunas >= 12:
            df_limpo["PC_RAW"] = df.iloc[:, 11].astype(str).str.strip()

        if qtd_colunas >= 13:
            df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()

        df_limpo = df_limpo[df_limpo["ID_JOGO"].str.isnumeric()]

        df_limpo["PP"] = pd.to_numeric(
            df_limpo["PP_RAW"], errors="coerce"
        ).fillna(0).astype(int)

        df_limpo["PC"] = pd.to_numeric(
            df_limpo["PC_RAW"], errors="coerce"
        ).fillna(0).astype(int)

        df_limpo = df_limpo.drop(columns=["PP_RAW", "PC_RAW"])

        return df_limpo.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao processar dados da tabela: {e}")
        return pd.DataFrame()


df_jogos = carregar_dados()

if not df_jogos.empty:

    st.write("### 🔍 Filtros de Pesquisa")

    f1, f2, f3 = st.columns(3)

    busca_data = f1.text_input(
        "🗓 Data",
        placeholder="Ex: 07/06"
    ).strip()

    busca_ano = f2.text_input(
        "📆 Ano",
        placeholder="Ex: 2026"
    ).strip()

    busca_categoria = f3.text_input(
        "🛡️ Categoria",
        placeholder="Ex: Adulto"
    ).strip()

    f4, f5, f6 = st.columns(3)

    busca_cidade = f4.text_input(
        "📍 Nossa Cidade",
        placeholder="Ex: São Paulo"
    ).strip()

    busca_adversario = f5.text_input(
        "⚔️ Adversário",
        placeholder="Ex: Locomotives"
    ).strip()

    busca_vd = f6.text_input(
        "🏆 Resultado (V / D / E)",
        placeholder="Ex: V"
    ).strip()

    df_filtrado = df_jogos.copy()

    if busca_data:
        df_filtrado = df_filtrado[
            df_filtrado["DATA"].str.contains(busca_data, na=False)
        ]

    if busca_ano:
        df_filtrado = df_filtrado[
            df_filtrado["ANO"].str.contains(busca_ano, na=False)
        ]

    if busca_categoria:
        df_filtrado = df_filtrado[
            df_filtrado["CATEGORIA"]
            .str.upper()
            .str.contains(busca_categoria.upper(), na=False)
        ]

    if busca_cidade:
        df_filtrado = df_filtrado[
            df_filtrado["CIDADE"]
            .str.upper()
            .str.contains(busca_cidade.upper(), na=False)
        ]

    if busca_adversario:
        df_filtrado = df_filtrado[
            df_filtrado["ADVERSARIO"]
            .str.upper()
            .str.contains(busca_adversario.upper(), na=False)
        ]

    if busca_vd:
        df_filtrado = df_filtrado[
            df_filtrado["VD"]
            .str.upper()
            .str.contains(busca_vd.upper(), na=False)
        ]

    st.markdown("---")

    if not df_filtrado.empty:

        df_filtrado = df_filtrado.reset_index(drop=True)

        st.write("### 📊 Indicadores Gerais")

        m1, m2, m3 = st.columns(3)

        total_jogos = len(df_filtrado)
        total_pp = int(df_filtrado["PP"].sum())
        total_pc = int(df_filtrado["PC"].sum())

        m1.metric(
            "Total de Partidas",
            total_jogos,
            f"De {len(df_jogos)} registradas"
        )

        m2.metric(
            "Pontos Pró Acumulados (PP)",
            total_pp,
            "Pontos Feitos"
        )

        m3.metric(
            "Pontos Contra Acumulados (PC)",
            total_pc,
            "- Pontos Sofridos",
            delta_color="inverse"
        )

        st.markdown("---")

        st.write("### 📈 Histórico Dinâmico de Atividade")

        df_filtrado["Periodo"] = (
            df_filtrado["DATA"].str.slice(3, 5)
            + "/"
            + df_filtrado["ANO"]
        )

        df_agrupado = (
            df_filtrado
            .groupby("Periodo")
            .agg(
                Qtd_Jogos=("ID_JOGO", "count"),
                Media_PP=("PP", "mean")
            )
            .reset_index()
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Volume de Jogos",
                x=df_agrupado["Periodo"],
                y=df_agrupado["Qtd_Jogos"],
                text=df_agrupado["Qtd_Jogos"],
                textposition="auto"
            )
        )

        fig.add_trace(
            go.Scatter(
                name="Média PP",
                x=df_agrupado["Periodo"],
                y=df_agrupado["Media_PP"],
                mode="lines+markers"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(
            "Nenhum dado corresponde aos filtros aplicados."
        )

else:
    st.error(
        "Arquivo dados.csv não encontrado ou sem dados válidos."
    )
