# ⚠️ PATCH para compatibilidade com phi em Python 3.11+
import inspect
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

import streamlit as st
import pandas as pd
import altair as alt
import re
from dotenv import load_dotenv
import os
from phi.agent import Agent
from phi.model.groq import Groq
from datetime import datetime

# 🔐 Carrega variáveis de ambiente
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY") or ""

# 🧠 Inicializa modelo Groq com deepseek-r1-distill-llama-70b
modelo_llm = Groq(id="deepseek-r1-distill-llama-70b")

# Criação do agente
agente = Agent(
    name="Analista de Estoque IA",
    role="Especialista em Vendas e Otimização de Estoque",
    model=modelo_llm,
    instructions=[
        "Fale em português.",
        "Analise séries temporais semanais de vendas por produto.",
        "Dê uma recomendação objetiva: Comprar, Não Comprar ou Analisar com Mais Cuidado.",
        "Justifique com base em volume, consistência, sazonalidade e faturamento.",
        "Responda no formato: Recomendação: ... / Motivo: ...",
        "Evite qualquer marcação de sistema como <system> ou <think>.",
    ],
    markdown=True
)

# 🌐 Configuração da interface
st.set_page_config(page_title="Otimizador de Estoque IA", layout="wide")
st.markdown("<h1 style='color:#00BFFF;'>📊 Otimizador de Estoque com IA</h1>", unsafe_allow_html=True)
st.markdown("🤖 <b>Analista de Estoque IA</b> pronto para te ajudar a decidir o que comprar!", unsafe_allow_html=True)

# Função para extrair semana
def extrair_semana(data_str):
    return pd.to_datetime(data_str, dayfirst=True).isocalendar().week

# 🧠 Cache de carregamento e pré-processamento
@st.cache_data
def carregar_dados(uploaded_file):
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
    df = df[["Quebra", "Quebra2", "Descrição", "Quantidade", "Faturamento"]]
    df["Semana"] = df["Quebra"].apply(extrair_semana)
    df["Quantidade"] = df["Quantidade"].str.replace(",", ".").astype(float)
    df["Faturamento"] = df["Faturamento"].str.replace(",", ".").astype(float)
    df["Semana"] = df["Semana"].astype(int)
    df["Quebra2"] = df["Quebra2"].astype("category")
    return df

# Tabs de navegação
tab1, tab2, tab3 = st.tabs(["📁 Upload de CSV", "🛠️ Filtros", "📊 Análise de Produtos"])

df = None
produtos_selecionados = []

# 📁 TAB 1: Upload
with tab1:
    uploaded_file = st.file_uploader("Envie o arquivo CSV com dados de vendas", type="csv")

if uploaded_file:
    with st.spinner("⏳ Carregando dados..."):
        df = carregar_dados(uploaded_file)

    # 🛠️ TAB 2: Filtros
    with tab2:
        st.markdown("### 🎯 Filtros")
        col1, col2 = st.columns(2)
        fornecedor = col1.selectbox("Selecione o fornecedor", df["Quebra2"].unique())
        semanas = sorted(df["Semana"].unique())
        semana_inicio, semana_fim = col2.select_slider("Intervalo de semanas",
                                                        options=semanas,
                                                        value=(min(semanas), max(semanas)))
        df_filtro = df[
            (df["Quebra2"] == fornecedor) & 
            (df["Semana"].between(semana_inicio, semana_fim))
        ]
        produtos_disponiveis = df_filtro["Descrição"].unique()
        produtos_selecionados = st.multiselect("🛒 Produtos para Análise", produtos_disponiveis)

    # 📊 TAB 3: Análise
    with tab3:
        if st.button("🚀 Gerar Análise dos Produtos") and produtos_selecionados:
            relatorios = []
            st.subheader("📑 Relatórios por Produto")

            for idx, produto in enumerate(produtos_selecionados):
                df_prod = df_filtro[df_filtro["Descrição"] == produto]
                vendas = df_prod.groupby("Semana")[["Quantidade", "Faturamento"]].sum().reset_index()

                # Limita análise para últimas 52 semanas (caso necessário)
                if len(vendas) > 52:
                    vendas = vendas.tail(52)

                resumo = f"""
Produto: {produto}
Fornecedor: {fornecedor}
Média Quantidade: {vendas['Quantidade'].mean():.2f}
Média Faturamento: R$ {vendas['Faturamento'].mean():.2f}
Total Faturado: R$ {vendas['Faturamento'].sum():.2f}
"""

                prompt = f"""
Você é um analista de dados de varejo. Com base nas vendas semanais do produto "{produto}", fornecido por "{fornecedor}", gere:

- Recomendação: "Comprar", "Não Comprar" ou "Analisar com Mais Cuidado"
- Motivo: explique com base em sazonalidade, faturamento total, média semanal e consistência de vendas.

Resumo dos dados:
{resumo}

Formato:
Recomendação: ...
Motivo: ...
"""
                try:
                    with st.spinner(f"🧠 Analisando {produto}..."):
                        resposta = agente.run(prompt)
                        texto_limpo = re.sub(r"<[^>]+>", "", resposta.content if hasattr(resposta, 'content') else resposta).strip()
                except Exception as e:
                    texto_limpo = f"❌ Erro na análise do produto: {e}"

                lower = texto_limpo.lower()
                if "não comprar" in lower or "nao comprar" in lower:
                    decisao = "Não Comprar"
                    cor_decisao = "red"
                elif "comprar" in lower:
                    decisao = "Comprar"
                    cor_decisao = "green"
                else:
                    decisao = "Analisar"
                    cor_decisao = "orange"

                relatorios.append({
                    "Produto": produto,
                    "Quantidade Total": vendas["Quantidade"].sum(),
                    "Faturamento Total": vendas["Faturamento"].sum(),
                    "Recomendação": decisao
                })

                st.markdown(f"""
                <div style='border:1px solid #ccc; border-radius:10px; padding:15px; background-color:#000000; margin-bottom:10px'>
                <h4>📦 {produto}</h4>
                <b>Recomendação:</b> <span style='color:{cor_decisao}'>{decisao}</span><br>
                <b>Faturamento Total:</b> R$ {vendas["Faturamento"].sum():,.2f}<br>
                <b>Quantidade Total:</b> {vendas["Quantidade"].sum():,.2f}
                </div>
                """, unsafe_allow_html=True)

                st.text_area("📘 Relatório Gerado", value=texto_limpo, height=300, key=f"rel{idx}")

                metrica = st.radio(
                    f"📈 Métrica para gráfico de {produto}",
                    options=["Quantidade", "Faturamento"],
                    key=f"metrica_{idx}"
                )

                chart = alt.Chart(vendas).mark_line(point=True).encode(
                    x="Semana:O",
                    y=alt.Y(f"{metrica}:Q", title=metrica),
                    tooltip=["Semana", "Quantidade", "Faturamento"]
                ).properties(title=f"Tendência Semanal - {produto}")

                st.altair_chart(chart, use_container_width=True)

            st.subheader("📋 Resumo Final das Recomendações")
            df_resumo = pd.DataFrame(relatorios)

            def cor_recomendacao(valor):
                cores = {"Comprar": "green", "Não Comprar": "red", "Analisar": "orange"}
                return f"color: {cores.get(valor, 'black')}"

            st.dataframe(
                df_resumo.sort_values(by="Faturamento Total", ascending=False).style.applymap(
                    cor_recomendacao, subset=["Recomendação"]
                ),
                use_container_width=True
            )

            st.subheader("🏆 Top 3 Produtos com Maior Faturamento")
            top3 = df_resumo.sort_values("Faturamento Total", ascending=False).head(3)
            cols = st.columns(len(top3))

            for i, row in enumerate(top3.itertuples()):
                cols[i].metric(
                    label=row.Produto,
                    value=f"R$ {row._3:,.2f}",
                    delta=row.Recomendação
                )

            st.success("✅ Análise concluída com sucesso!")
