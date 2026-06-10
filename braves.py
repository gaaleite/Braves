import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.request
import io

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# Injeta CSS para aplicar o fundo azul-marinho profundo e ajustar os textos para branco
css_fundo_azul_marinho = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0a192f; /* Azul-marinho profundo e profissional */
}
/* Força títulos e subtextos principais a ficarem brancos */
h1, h2, h3, p, span, label, [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}
/* Altera as letras digitadas dentro das caixas de filtro para branco */
input, select, div[data-baseweb="select"] * {
    color: #ffffff !important;
}
</style>
"""
st.markdown(css_fundo_azul_marinho, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        # Link oficial fornecido
        url_original = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNg8QGIcR3oocTpka0agajCb-CF37OWvuJuG66FeMrhgAOY6qpg8zlej9iGK7dTQ1jQX8Gc_VahDPo/pubhtml?gid=516798055&single=true"
        
        # Correção do link: substituição direta e segura de texto sem gerar listas corrompidas
        url_csv = url_original.replace("/pubhtml", "/pub")
        if "&output=csv" not in url_csv:
            url_csv += "&output=csv"
        
        # Faz a requisição simulando um navegador para evitar bloqueios de segurança do Google
        req = urllib.request.Request(url_csv, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            dados_brutos = response.read()
            
        # Lê o arquivo tratando o cabeçalho pelas posições das colunas (header=None) para controle total
        df = pd.read_csv(io.BytesIO(dados_brutos), header=None, on_bad_lines="skip")
        
        if df.empty:
            return pd.DataFrame()

        qtd_colunas = len(df.columns)
        df_limpo = pd.DataFrame()

        # Mapeamento estrito baseado nas colunas reais da imagem enviada
        if qtd_colunas >= 1:
            df_limpo["JOGO"] = df.iloc[:, 0].astype(str).str.strip()
        if qtd_colunas >= 2:
            df_limpo["DATA"] = df.iloc[:, 1].astype(str).str.strip()
        if qtd_colunas >= 3:
            df_limpo["ANO"] = df.iloc[:, 2].astype(str).str.strip()
        if qtd_colunas >= 4:
            df_limpo["TORNEIO"] = df.iloc[:, 3].astype(str).str.strip()
        if qtd_colunas >= 5:
            df_limpo["FAIXA_ETARIA"] = df.iloc[:, 4].astype(str).str.strip() # Coluna "TIME" (Adulto, Sub 17, etc.)
        if qtd_colunas >= 6:
            df_limpo["CATEGORIA"] = df.iloc[:, 5].astype(str).str.strip() # Coluna "CATEGORIA" (5x5, 6x6)
        if qtd_colunas >= 7:
            df_limpo["CIDADE"] = df.iloc[:, 6].astype(str).str.strip()
        if qtd_colunas >= 8:
            df_limpo["ESTADO"] = df.iloc[:, 7].astype(str).str.strip()
        if qtd_colunas >= 9:
            df_limpo["VD"] = df.iloc[:, 8].astype(str).str.upper().str.strip()
        
        # Extrai os dados em formato de texto isoladamente antes de convertê-los em números
        pp_raw = df.iloc[:, 10].astype(str).str.strip() if qtd_colunas >= 11 else "0"
        pc_raw = df.iloc[:, 11].astype(str).str.strip() if qtd_colunas >= 12 else "0"
        
        if qtd_colunas >= 13:
            df_limpo["ADVERSARIO"] = df.iloc[:, 12].astype(str).str.strip()
        else:
            df_limpo["ADVERSARIO"] = "Desconhecido"

        # Remove a linha de títulos (onde a primeira coluna diz "JOGO") mantendo apenas IDs numéricos válidos
        df_limpo = df_limpo[df_limpo["JOGO"].str.isnumeric()]

        # Converte placares com segurança apenas para as linhas numéricas válidas filtradas
        df_limpo["PP"] = pd.to_numeric(pp_raw.loc[df_limpo.index], errors="coerce").fillna(0).astype(int)
        df_limpo["PC"] = pd.to_numeric(pc_raw.loc[df_limpo.index], errors="coerce").fillna(0).astype(int)

        return df_limpo.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao processar dados da tabela: {e}")
        return pd.DataFrame()

# Chamada principal de processamento dos dados
df_jogos = carregar_dados()

if df_jogos.empty:
    st.error("⚠️ O banco de dados retornou vazio. Verifique se o link foi publicado corretamente no menu do Drive.")
else:
    st.write("### 🔍 Filtros de Pesquisa")

    # Filtros estruturados em colunas paralelas
    f1, f2, f3 = st.columns(3)
    busca_data = f1.text_input("🗓 Data", placeholder="Ex: 07/06").strip()
    busca_ano = f2.text_input("📆 Ano", placeholder="Ex: 2026").strip()
    
    # Dropdown automático para selecionar a categoria (Adulto, Sub 14, Sub 17, etc.)
    opcoes_time = ["Todos"] + sorted(list(df_jogos["FAIXA_ETARIA"].unique()))
    busca_time_categoria = f3.selectbox("🛡️ Time (Categoria)", opcoes_time)

    f4, f5, f6 = st.columns(3)
    busca_cidade = f4.text_input("📍 Nossa Cidade", placeholder="Ex: São Paulo").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: Locomotives").strip()
    busca_vd = f6.text_input("🏆 Resultado (V / D)", placeholder="Ex: V").strip()

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

        df_grafico = df_filtrado.copy()
        df_grafico["ID_NUM"] = pd.to_numeric(df_grafico["JOGO"], errors="coerce")
        df_grafico = df_grafico.sort_values(by="ID_NUM", ascending=False)

        df_grafico["Rotulo_Jogo"] = (
            "Jogo " + df_grafico["JOGO"] + "<br>" + 
            df_grafico["DATA"]
        )

        # Lógica para definir a cor de cada barra individualmente com base no placar
        cores_barras = []
        for pp, pc in zip(df_grafico["PP"], df_grafico["PC"]):
            if pp > pc:
                cores_barras.append("#2ece7d")  # Verde suave para Vitória
            elif pp < pc:
                cores_barras.append("#e74c3c")  # Vermelho suave para Derrota
            else:
                cores_barras.append("#f1c40f")  # Amarelo suave para Empate

        try:
            fig = go.Figure()
            valores_y = [1] * len(df_grafico)
            
            fig.add_trace(
                go.Bar(
                    name="Jogos",
                    x=[df_grafico["ANO"], df_grafico["Rotulo_Jogo"]],
                    y=valores_y,
                    text=[f"{pp}x{pc}" for pp, pc in zip(df_grafico["PP"], df_grafico["PC"])],
                    textposition="outside",
                    marker=dict(
                        color=cores_barras,
                        line=dict(color="#778899", width=1)
                    )
                )
            )
            
            # Força os textos de baixo a ficarem retos na horizontal
            fig.update_layout(
                xaxis=dict(tickangle=0)
            )
            
            st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Erro ao gerar o gráfico dinâmico: {e}")


            titulo_dinamico = f"Evolução de Atividade — Total de {len(df_grafico)} Partidas Realizadas"
            
            fig.update_layout(
                title=dict(
                    text=titulo_dinamico,
                    x=0.5,
                    xanchor="center",
                    font=dict(family="sans-serif", size=14, color="#202122", weight="bold")
                ),
                paper_bgcolor="#E2EFFF",          
                plot_bgcolor="#E2EFFF",           
                margin=dict(l=40, r=40, t=60, b=80),
                showlegend=False,
                shapes=[
                    dict(
                        type="rect",
                        xref="paper", yref="paper",
                        x0=0, y0=0, x1=1, y1=1,
                        line=dict(color="#a2a9b1", width=1)
                    )
                ]
            )
            
            fig.update_xaxes(
                title_text="Temporada / Partida", 
                tickangle=0,
                title_font=dict(color="black"),
                tickfont=dict(family="sans-serif", size=10, color="black")
            )
            fig.update_yaxes(showticklabels=False, showgrid=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao renderizar o gráfico: {e}")
        
        st.write("### 📋 Tabela de Dados Filtrada")
        colunas_exibicao = ["JOGO", "DATA", "ANO", "TORNEIO", "FAIXA_ETARIA", "CATEGORIA", "CIDADE", "VD", "PP", "PC", "ADVERSARIO"]
        st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)
        
    else:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
