import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import SheetsConnection

st.set_page_config(layout="wide", page_title="Braves Analytics")
st.title("🏈 Braves Academy - Painel de Controle")

# Configuração da conexão com o Google Sheets
# Nota: Requer configuração de service_account no .streamlit/secrets.toml para escrita
try:
    conn = st.connection("gsheets", type=SheetsConnection)
except Exception:
    conn = None

@st.cache_data(ttl=10)
def carregar_dados_posicionais():
    if conn is None:
        return pd.DataFrame()
    try:
        # Lê os dados em tempo real usando a conexão oficial do Streamlit
        df = conn.read(ttl="10s")
        
        if not df.empty:
            qtd_colunas = len(df.columns)
            df_limpo = pd.DataFrame()
            
            # Mapeamento exato baseado nos seus índices físicos (ajustados para 0)
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
            
            # Limpeza contra scripts e nulos
            df_limpo = df_limpo[~df_limpo["JOGO"].str.contains(r"\{|function|var|index|void|call|html", case=False, na=True)]
            df_limpo = df_limpo[df_limpo["JOGO"] != "nan"]
            df_limpo = df_limpo[df_limpo["JOGO"] != ""]
            
            return df_limpo.reset_index(drop=True)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na conexão com os dados: {e}")
        return pd.DataFrame()

# Carrega os dados para o gráfico
df_jogos = carregar_dados_posicionais()

# --- CRIAÇÃO DAS ABAS ---
aba_graficos, aba_adicionar = st.tabs(["📊 Gráfico de Jogos", "➕ Adicionar Novo Jogo"])

# ==========================================
# CONTEÚDO DA ABA 1: GRÁFICOS
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
            st.info("Nenhum dado corresponde aos filtros.")
    else:
        st.warning("Aguardando conexão ou configuração das credenciais do Sheets.")

# ==========================================
# CONTEÚDO DA ABA 2: FORMULÁRIO DE CADASTRO
# ==========================================
with aba_adicionar:
    st.write("### 📝 Cadastrar Nova Partida")
    st.caption("Preencha os campos abaixo para salvar as informações diretamente na planilha do Google.")

    # Criação do formulário estruturado por colunas
    with st.form(key="formulario_jogo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        input_data = c1.text_input("🗓 Data do Jogo", placeholder="Ex: 12/05")
        input_ano = c2.text_input("📆 Ano", placeholder="Ex: 2026")
        input_jogo = c3.text_input("🔢 Número do Jogo (ID)", placeholder="Ex: 42")
        
        c4, c5, c6 = st.columns(3)
        input_time = c4.text_input("🛡️ Categoria / Nosso Time", placeholder="Ex: Sub 14")
        input_adversario = c5.text_input("⚔️ Adversário", placeholder="Ex: Fox")
        input_vd = c6.selectbox("🏆 Resultado", ["V", "D", "E"], help="V = Vitória, D = Derrota, E = Empate")
        
        c7, c8, c9 = st.columns(3)
        input_cidade = c7.text_input("📍 Cidade", placeholder="Ex: Sorocaba")
        input_estado = c8.text_input("🏳️ Estado (UF)", placeholder="Ex: SP", max_chars=2)
        
        c10, c11 = st.columns(2)
        input_pp = c10.number_input("🟢 Pontos Pró (PP)", min_value=0, step=1, value=0)
        input_pc = c11.number_input("🔴 Pontos Contra (PC)", min_value=0, step=1, value=0)
        
        # Botão de envio
        botao_salvar = st.form_submit_button(label="💾 Salvar no Google Sheets")
        
        if botao_salvar:
            if not input_jogo or not input_time or not input_adversario:
                st.error("⚠️ Os campos 'Número do Jogo', 'Time' e 'Adversário' são obrigatórios!")
            elif conn is None:
                st.error("❌ Conexão com o Google Sheets não configurada.")
            else:
                try:
                    # Carrega a planilha bruta atual
                    df_atual = conn.read()
                    
                    # Cria a nova linha respeitando a ordem exata das suas colunas na planilha original:
                    # Índice 0: ID/Vazio, 1: DATA, 2: ANO, 3: JOGO, 4: TIME, 5: Vazio, 6: CIDADE, 7: ESTADO, 8: VD, 9: Vazio, 10: PP, 11: PC, 12: ADVERSARIO
                    nova_linha = {
                        df_atual.columns[1]: input_data,
                        df_atual.columns[2]: input_ano,
                        df_atual.columns[3]: input_jogo,
                        df_atual.columns[4]: input_time,
                        df_atual.columns[6]: input_cidade,
                        df_atual.columns[7]: input_estado,
                        df_atual.columns[8]: input_vd,
                        df_atual.columns[10]: input_pp,
                        df_atual.columns[11]: input_pc,
                        df_atual.columns[12]: input_adversario
                    }
                    
                    # Converte em DataFrame e concatena
                    df_nova_linha = pd.DataFrame([nova_linha])
                    df_atualizado = pd.concat([df_atual, df_nova_linha], ignore_index=True)
                    
                    # Grava de volta na nuvem
                    conn.update(data=df_atualizado)
                    
                    st.success("✅ Partida adicionada com sucesso! O gráfico será atualizado.")
                    st.cache_data.clear() # Limpa o cache para forçar a releitura do gráfico
                    
                except Exception as e:
                    st.error(f"Erro ao salvar dados no Google Sheets: {e}")
