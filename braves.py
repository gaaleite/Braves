import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.request
import io

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        # URL forçando a exportação direta em CSV puro (rápido e sem depender de HTML/lxml)
        url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNg8QGIcR3oocTpka0agajCb-CF37OWvuJuG66FeMrhgAOY6qpg8zlej9iGK7dTQ1jQX8Gc_VahDPo/pubhtml?gid=516798055&single=true"
        
        # Requisição nativa para baixar os dados
        req = urllib.request.Request(url_csv, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            dados_brutos = response.read()
            
        # Carrega o CSV tratando a primeira linha válida como cabeçalho de nomes
        df = pd.read_csv(io.BytesIO(dados_brutos), on_bad_lines="skip")
        
        if df.empty:
            return pd.DataFrame()

        # Limpa os nomes das colunas (remove espaços em branco e deixa tudo em maiúsculo)
        df.columns = df.columns.astype(str).str.strip().str.upper()
        
        df_limpo = pd.DataFrame()

        # Identificação e mapeamento dinâmico por nome de coluna (evita erros de índice fora de alcance)
        # ID do Jogo (Geralmente a primeira coluna da tabela)
        df_limpo["ID_JOGO"] = df.iloc[:, 0].astype(str).str.strip()
        
        # Captura segura mapeando termos comuns ou variações de digitação na planilha
        colunas = df.columns
        
        df_limpo["DATA"] = df["DATA"].astype(str).str.strip() if "DATA" in colunas else ""
        df_limpo["ANO"] = df["ANO"].astype(str).str.strip() if "ANO" in colunas else ""
        df_limpo["TORNEIO"] = df["TORNEIO"].astype(str).str.strip() if "TORNEIO" in colunas else ""
        df_limpo["CATEGORIA"] = df["CATEGORIA"].astype(str).str.strip() if "CATEGORIA" in colunas else ""
        df_limpo["LOCAL"] = df["LOCAL"].astype(str).str.strip() if "LOCAL" in colunas else ""
        df_limpo["CIDADE"] = df["CIDADE"].astype(str).str.strip() if "CIDADE" in colunas else ""
        df_limpo["ESTADO"] = df["ESTADO"].astype(str).str.strip() if "ESTADO" in colunas else ""
        
        # Mapeamento do resultado do jogo (V / D / E)
        if "V / D / E" in colunas:
            df_limpo["VD"] = df["V / D / E"].astype(str).str.upper().str.strip()
        elif "VD" in colunas:
            df_limpo["VD"] = df["VD"].astype(str).str.upper().str.strip()
        else:
            df_limpo["VD"] = ""

        # Mapeamento dinâmico para Pontos Pró (PP)
        if "PP" in colunas:
            df_limpo["PP"] = pd.to_numeric(df["PP"], errors="coerce").fillna(0).astype(int)
        else:
            df_limpo["PP"] = 0

        # Mapeamento dinâmico para Pontos Contra (PC)
        if "PC" in colunas:
            df_limpo["PC"] = pd.to_numeric(df["PC"], errors="coerce").fillna(0).astype(int)
        else:
            df_limpo["PC"] = 0

        # Mapeamento dinâmico para o Adversário
        if "ADVERSÁRIO" in colunas:
            df_limpo["ADVERSARIO"] = df["ADVERSÁRIO"].astype(str).str.strip()
        elif "ADVERSARIO" in colunas:
            df_limpo["ADVERSARIO"] = df["ADVERSARIO"].astype(str).str.strip()
        else:
            df_limpo["ADVERSARIO"] = "Desconhecido"

        # Remove linhas de cabeçalho extras ou vazias filtrando apenas registros onde o ID é numérico
        df_limpo = df_limpo[df_limpo["ID_JOGO"].str.isnumeric()]

        return df_limpo.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao processar dados da tabela: {e}")
        return pd.DataFrame()

# Executa o carregamento dos dados
df_jogos = carregar_dados()

if df_jogos.empty:
    st.error("⚠️ Não foi possível ler os dados da planilha. Verifique se ela continua publicada na web corretamente no Google Sheets.")
else:
    st.write("### 🔍 Filtros de Pesquisa")

    # Layout de colunas para os filtros de texto
    f1, f2, f3 = st.columns(3)
    busca_data = f1.text_input("🗓 Data", placeholder="Ex: 07/06").strip()
    busca_ano = f2.text_input("📆 Ano", placeholder="Ex: 2026").strip()
    busca_categoria = f3.text_input("🛡️ Categoria", placeholder="Ex: Adulto").strip()

    f4, f5, f6 = st.columns(3)
    busca_cidade = f4.text_input("📍 Nossa Cidade", placeholder="Ex: São Paulo").strip()
    busca_adversario = f5.text_input("⚔️ Adversário", placeholder="Ex: Locomotives").strip()
    busca_vd = f6.text_input("🏆 Resultado (V / D / E)", placeholder="Ex: V").strip()

    # Aplicação dos filtros no DataFrame secundário
    df_filtrado = df_jogos.copy()

    if busca_data:
        df_filtrado = df_filtrado[df_filtrado["DATA"].str.contains(busca_data, na=False)]
    if busca_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO"].str.contains(busca_ano, na=False)]
    if busca_categoria:
        df_filtrado = df_filtrado[df_filtrado["CATEGORIA"].str.upper().str.contains(busca_categoria.upper(), na=False)]
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

        # Configuração do gráfico em ordem cronológica decrescente
        df_grafico = df_filtrado.copy()
        df_grafico["ID_NUM"] = pd.to_numeric(df_grafico["ID_JOGO"], errors="coerce")
        df_grafico = df_grafico.sort_values(by="ID_NUM", ascending=False)

        df_grafico["Rotulo_Jogo"] = (
            "Jogo " + df_grafico["ID_JOGO"] + "<br>" + 
            df_grafico["DATA"] + "<br>vs " + df_grafico["ADVERSARIO"]
        )

        try:
            fig = go.Figure()
            
            # Altura das barras padronizada por tamanho do lote de dados
            valores_y = [1] * len(df_grafico)
            
            fig.add_trace(
                go.Bar(
                    name="Jogos",
                    x=[df_grafico["ANO"], df_grafico["Rotulo_Jogo"]],
                    y=valores_y,
                    text=[f"{pp}x{pc}" for pp, pc in zip(df_grafico["PP"], df_grafico["PC"])],
                    textposition="outside",
                    marker=dict(color="#b0c4de", line=dict(color="#778899", width=1)),
                    textfont=dict(family="sans-serif", size=10, color="#202122")
                )
            )

            titulo_dinamico = f"Evolução de Atividade — Total de {len(df_grafico)} Partidas Realizadas"
            
            fig.update_layout(
                title=dict(
                    text=titulo_dinamico,
                    x=0.5,
                    xanchor="center",
                    font=dict(family="sans-serif", size=14, color="#202122", weight="bold")
                ),
                backgroundcolor="#f8f9fa",
                paper_bgcolor="#f8f9fa",          
                plot_bgcolor="#f8f9fa",           
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
            
            fig.update_xaxes(title_text="Temporada / Partida", tickangle=0)
            fig.update_yaxes(showticklabels=False, showgrid=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao renderizar o gráfico: {e}")
        
        st.write("### 📋 Tabela de Dados Filtrada")
        colunas_exibicao = ["ID_JOGO", "DATA", "ANO", "TORNEIO", "CATEGORIA", "CIDADE", "VD", "PP", "PC", "ADVERSARIO"]
        st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)
        
    else:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
