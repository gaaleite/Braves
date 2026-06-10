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

        # 1. Preparação dos dados e ordenação: do jogo mais atual para o mais antigo
        # Convertemos o ID_JOGO para numérico para garantir a ordenação cronológica decrescente correta
        df_grafico = df_filtrado.copy()
        df_grafico["ID_NUM"] = pd.to_numeric(df_grafico["ID_JOGO"], errors="coerce")
        df_grafico = df_grafico.sort_values(by="ID_NUM", ascending=False)

        # Criamos o rótulo do nome de cada dado que vai aparecer na parte de baixo do gráfico
        df_grafico["Rotulo_Jogo"] = (
            "Jógo " + df_grafico["ID_JOGO"] + "<br>" + 
            df_grafico["DATA"] + "<br>vs " + df_grafico["ADVERSARIO"]
        )

        # Calcular o total de jogos por ano para exibir no gráfico de forma dinâmica
        total_por_ano = df_grafico.groupby("ANO")["ID_JOGO"].count().to_dict()

        fig = go.Figure()

        # 2. Plotagem das barras no estilo clássico Wikipédia (IBGE)
        # Usamos uma lista multi-nível nos eixos (ANO, Rotulo) para criar a separação visual por colunas de anos
        fig.add_trace(
            go.Bar(
                name="Jogos",
                x=[df_grafico["ANO"], df_grafico["Rotulo_Jogo"]],
                y=[1] * len(df_grafico), # Cada jogo individual representa 1 unidade no bloco do censo
                text=[f"Placar: {pp}x{pc}" for pp, pc in zip(df_grafico["PP"], df_grafico["PC"])],
                textposition="outside",
                marker=dict(
                    color="#b0c4de",          # Azul-aço clássico da Wikipédia
                    line=dict(
                        color="#778899",      # Borda cinza escuro
                        width=1
                    )
                ),
                textfont=dict(
                    family="sans-serif",
                    size=10,
                    color="#202122"
                )
            )
        )

        # 3. Customização do Layout simulando a caixa de evolução populacional da Wikipédia
        # Título dinâmico que puxa o tamanho total atual do dataframe (ex: 277 jogos)
        titulo_dinamico = f"Evolução de Atividade — Total de {len(df_grafico)} Partidas Realizadas"
        
        fig.update_layout(
            title=dict(
                text=titulo_dinamico,
                x=0.5,
                xanchor="center",
                font=dict(
                    family="sans-serif",
                    size=14,
                    color="#202122",
                    weight="bold"
                )
            ),
            backgroundcolor="#f8f9fa",        # Cor de fundo padrão cinza claro das tabelas wiki
            paper_bgcolor="#f8f9fa",          
            plot_bgcolor="#f8f9fa",           
            margin=dict(l=40, r=40, t=60, b=80),
            showlegend=False,
            # Gera a borda cinza externa do infobox
            shapes=[
                dict(
                    type="rect",
                    xref="paper", yref="paper",
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color="#a2a9b1", width=1)
                )
            ]
        )

        # 4. Ajuste dos Eixos com agrupamento e nomes na parte inferior
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#d3d3d3",              # Grade vertical para separar claramente as colunas dos anos
            linecolor="#54595d",              # Linha escura espessa na base inferior
            linewidth=2,
            tickangle=0,
            font=dict(
                family="sans-serif",
                size=11,
                color="#202122"
            )
        )

        # Como a contagem é por blocos de jogo, escondemos os números do eixo Y para focar nos nomes inferiores
        fig.update_yaxes(
            showgrid=False,
            showticklabels=False,
            linecolor="#a2a9b1",
            linewidth=1
        )

        # 5. Adiciona anotações no topo do gráfico mostrando o total acumulado de cada ano de forma limpa
        for ano, total in total_por_ano.items():
            fig.add_annotation(
                text=f"<b>Ano {ano}<br>Total: {total} jogos</b>",
                xref="x",
                yref="paper",
                x=(ano, df_grafico[df_grafico["ANO"] == ano]["Rotulo_Jogo"].iloc[0]),
                y=1.05,
                showarrow=False,
                font=dict(family="sans-serif", size=11, color="#202122")
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
