import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
import os
from groq import Groq

# =====================
# CONFIGURAÇÃO INICIAL
# =====================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Otimizador de Estoque IA", layout="wide")
st.markdown("<h1 style='color:#00BFFF;'>📊 Otimizador de Estoque com IA</h1>", unsafe_allow_html=True)
st.markdown("🤖 <b>Analista de Estoque IA (Groq)</b>", unsafe_allow_html=True)

# =====================
# FUNÇÕES
# =====================
def extrair_semana(data_str):
    return pd.to_datetime(data_str, dayfirst=True).isocalendar().week

@st.cache_data
def carregar_dados(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, sep=";", encoding="iso-8859-1")

    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Data": "Data",
        "Fornecedor": "Fornecedor",
        "Descrição": "Descrição",
        "Quantidade Vendida": "Quantidade",
        "Preço de Venda": "Faturamento",
        "Preço de Custo": "Custo"
    })

    df["Semana"] = df["Data"].apply(extrair_semana)
    df["Quantidade"] = df["Quantidade"].astype(str).str.replace(",", ".").astype(float)
    df["Faturamento"] = df["Faturamento"].astype(str).str.replace(",", ".").astype(float)
    df["Fornecedor"] = df["Fornecedor"].astype("category")

    return df

# =====================
# SESSION STATE
# =====================
if "analise_gerada" not in st.session_state:
    st.session_state.analise_gerada = False
    st.session_state.resultados = {}
    st.session_state.resumo_final = []

# =====================
# TABS
# =====================
tab1, tab2, tab3 = st.tabs(["📁 Upload", "🛠️ Filtros", "📊 Análise"])

# =====================
# TAB 1 - UPLOAD
# =====================
with tab1:
    uploaded_file = st.file_uploader("Envie o CSV de vendas", type="csv")

if uploaded_file:
    df = carregar_dados(uploaded_file)

    # =====================
    # TAB 2 - FILTROS
    # =====================
    with tab2:
        col1, col2 = st.columns(2)
        fornecedor = col1.selectbox("Fornecedor", df["Fornecedor"].unique())

        semanas = sorted(df["Semana"].unique())
        semana_inicio, semana_fim = col2.select_slider(
            "Intervalo de semanas",
            options=semanas,
            value=(min(semanas), max(semanas))
        )

        df_filtro = df[
            (df["Fornecedor"] == fornecedor) &
            (df["Semana"].between(semana_inicio, semana_fim))
        ]

        produtos_selecionados = st.multiselect(
            "Produtos para análise",
            df_filtro["Descrição"].unique()
        )

    # =====================
    # TAB 3 - ANÁLISE
    # =====================
    with tab3:
        if st.button("🚀 Gerar Análise") and produtos_selecionados:
            st.session_state.analise_gerada = True
            st.session_state.resultados = {}
            st.session_state.resumo_final = []

            for produto in produtos_selecionados:
                df_prod = df_filtro[df_filtro["Descrição"] == produto]
                vendas = df_prod.groupby("Semana")[["Quantidade", "Faturamento"]].sum().reset_index()

                if len(vendas) > 52:
                    vendas = vendas.tail(52)

                resumo = f"""
Produto: {produto}
Fornecedor: {fornecedor}
Média semanal vendida: {vendas['Quantidade'].mean():.2f}
Média faturamento semanal: R$ {vendas['Faturamento'].mean():.2f}
Total faturado: R$ {vendas['Faturamento'].sum():.2f}
Semanas analisadas: {len(vendas)}
"""

                prompt = f"""
Você é um analista de estoque.

Com base nos dados abaixo, gere:
- Recomendação: Comprar, Não Comprar ou Analisar com Mais Cuidado
- Motivo: claro e objetivo

Dados:
{resumo}

Formato:
Recomendação: ...
Motivo: ...
"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Especialista em gestão de estoque."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                texto = response.choices[0].message.content
                texto_lower = texto.lower()

                if "não comprar" in texto_lower or "nao comprar" in texto_lower:
                    decisao = "Não Comprar"
                elif "comprar" in texto_lower:
                    decisao = "Comprar"
                else:
                    decisao = "Analisar"

                st.session_state.resultados[produto] = {
                    "vendas": vendas,
                    "texto": texto,
                    "decisao": decisao
                }

                st.session_state.resumo_final.append({
                    "Produto": produto,
                    "Quantidade Total": vendas["Quantidade"].sum(),
                    "Faturamento Total": vendas["Faturamento"].sum(),
                    "Recomendação": decisao
                })

        # =====================
        # EXIBIÇÃO (REAGENTE)
        # =====================
        if st.session_state.analise_gerada:
            for produto, dados in st.session_state.resultados.items():
                vendas = dados["vendas"]
                decisao = dados["decisao"]
                texto = dados["texto"]

                cor = {"Comprar": "green", "Não Comprar": "red", "Analisar": "orange"}[decisao]

                st.markdown(f"""
                <div style='border:1px solid #444; border-radius:10px; padding:15px; background:#000'>
                <h4>{produto}</h4>
                <b>Recomendação:</b> <span style='color:{cor}'>{decisao}</span><br>
                <b>Faturamento:</b> R$ {vendas["Faturamento"].sum():,.2f}<br>
                <b>Quantidade:</b> {vendas["Quantidade"].sum():,.2f}
                </div>
                """, unsafe_allow_html=True)

                st.text_area("Relatório IA", texto, height=160, key=f"txt_{produto}")

                metrica = st.radio(
                    f"Métrica do gráfico - {produto}",
                    ["Quantidade", "Faturamento"],
                    key=f"metrica_{produto}"
                )

                chart = alt.Chart(vendas).mark_line(point=True).encode(
                    x="Semana:O",
                    y=f"{metrica}:Q",
                    tooltip=["Semana", "Quantidade", "Faturamento"]
                ).properties(title=f"Tendência - {produto}")

                st.altair_chart(chart, use_container_width=True)

            st.subheader("📋 Resumo Final")

            df_resumo = pd.DataFrame(st.session_state.resumo_final)

            def estilo(valor):
                cores = {"Comprar": "green", "Não Comprar": "red", "Analisar": "orange"}
                return f"color: {cores.get(valor, 'black')}"

            st.dataframe(
                df_resumo
                .sort_values("Faturamento Total", ascending=False)
                .style.map(estilo, subset=["Recomendação"]),
                use_container_width=True
            )

            st.success("✅ Análise concluída com sucesso!")
