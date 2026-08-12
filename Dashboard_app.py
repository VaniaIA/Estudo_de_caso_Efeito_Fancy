import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Efeito Fancy",
    page_icon="✨",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    df = pd.read_csv("vendas_clientes_catalogo.csv")
    df["is_fancy"] = (
        df["linha"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("fancy")
    )
    return df

df = carregar_dados()

st.title("✨ Efeito Fancy")
st.markdown(
    "Dashboard para análise do Fancy Score, rentabilidade e público-alvo."
)

st.sidebar.header("Filtros")

estados = st.sidebar.multiselect(
    "Estado",
    sorted(df["estado"].dropna().unique()),
    default=sorted(df["estado"].dropna().unique())
)

canais = st.sidebar.multiselect(
    "Canal",
    sorted(df["canal_aquisicao"].dropna().unique()),
    default=sorted(df["canal_aquisicao"].dropna().unique())
)

categorias = st.sidebar.multiselect(
    "Categoria",
    sorted(df["categoria"].dropna().unique()),
    default=sorted(df["categoria"].dropna().unique())
)

df = df[
    df["estado"].isin(estados)
    & df["canal_aquisicao"].isin(canais)
    & df["categoria"].isin(categorias)
].copy()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

clientes = (
    df.groupby("id_cliente")
    .agg(
        total_compras=("id_pedido", "count"),
        compras_fancy=("is_fancy", "sum"),
        lucro_total=("Lucro Bruto", "sum"),
        idade=("idade", "first"),
        renda=("renda_mensal", "first")
    )
    .reset_index()
)

clientes["fancy_score"] = (
    clientes["compras_fancy"]
    / clientes["total_compras"]
    * 100
)

clientes["lucro_medio"] = (
    clientes["lucro_total"]
    / clientes["total_compras"]
)

st.header("📊 Indicadores")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Clientes",
    f"{len(clientes):,}".replace(",", ".")
)

c2.metric(
    "Compras",
    f"{len(df):,}".replace(",", ".")
)

c3.metric(
    "Fancy Score médio",
    f"{clientes['fancy_score'].mean():.2f}%"
)

c4.metric(
    "% Compras Fancy",
    f"{df['is_fancy'].mean() * 100:.2f}%"
)

st.divider()

st.header("1️⃣ Fancy Score")

st.markdown(
    """
    O Fancy Score mostra a porcentagem de compras Fancy realizadas
    por cada cliente.

    **Fancy Score = Compras Fancy ÷ Total de compras × 100**
    """
)

fig1 = px.histogram(
    clientes,
    x="fancy_score",
    nbins=20,
    title="Distribuição do Fancy Score",
    labels={
        "fancy_score": "Fancy Score (%)",
        "count": "Clientes"
    }
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

st.header("2️⃣ Efeito Fancy")

st.markdown(
    """
    Para verificar o Efeito Fancy, comparamos o Fancy Score com o
    lucro médio por compra de cada cliente.
    """
)

correlacao = clientes["fancy_score"].corr(
    clientes["lucro_medio"]
)

fig2 = px.scatter(
    clientes,
    x="fancy_score",
    y="lucro_medio",
    title="Fancy Score x Lucro Médio por Compra",
    labels={
        "fancy_score": "Fancy Score (%)",
        "lucro_medio": "Lucro médio por compra (R$)"
    },
    hover_data=[
        "id_cliente",
        "total_compras",
        "idade",
        "renda"
    ]
)

st.plotly_chart(fig2, use_container_width=True)

st.metric(
    "Correlação de Pearson",
    f"{correlacao:.3f}"
)

if correlacao >= 0.7:
    st.success(
        "Existe uma relação positiva forte entre Fancy Score e lucro."
    )
elif correlacao >= 0.3:
    st.info(
        "Existe uma relação positiva moderada entre Fancy Score e lucro."
    )
else:
    st.warning(
        "A relação entre as variáveis é fraca."
    )

st.markdown(
    f"""
    A correlação encontrada foi de **{correlacao:.3f}**.

    Isso indica uma associação positiva entre a participação de
    produtos Fancy nas compras e o lucro médio por compra.

    **Importante:** correlação não significa causalidade.
    """
)

st.divider()

st.header("3️⃣ Comparação entre grupos")

grupo_baixo = clientes[
    clientes["fancy_score"] < 50
]

grupo_alto = clientes[
    clientes["fancy_score"] >= 50
]

lucro_baixo = grupo_baixo["lucro_medio"].mean()
lucro_alto = grupo_alto["lucro_medio"].mean()

diferenca = (
    (lucro_alto - lucro_baixo)
    / lucro_baixo
    * 100
)

comparacao = pd.DataFrame({
    "Grupo": [
        "Fancy Score < 50%",
        "Fancy Score >= 50%"
    ],
    "Lucro": [
        lucro_baixo,
        lucro_alto
    ]
})

fig3 = px.bar(
    comparacao,
    x="Grupo",
    y="Lucro",
    text_auto=".2f",
    title="Lucro médio por grupo",
    labels={
        "Grupo": "Grupo",
        "Lucro": "Lucro médio por compra (R$)"
    }
)

st.plotly_chart(fig3, use_container_width=True)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Lucro < 50% Fancy",
    f"R$ {lucro_baixo:.2f}"
)

c2.metric(
    "Lucro >= 50% Fancy",
    f"R$ {lucro_alto:.2f}"
)

c3.metric(
    "Diferença",
    f"{diferenca:.1f}%"
)

st.divider()

st.header("4️⃣ Público-alvo recomendado")

percentual_alto = (
    len(grupo_alto)
    / len(clientes)
    * 100
)

idade_alto = grupo_alto["idade"].mean()
renda_alto = grupo_alto["renda"].mean()

c1, c2, c3 = st.columns(3)

c1.metric(
    "Clientes >= 50% Fancy",
    f"{percentual_alto:.1f}%"
)

c2.metric(
    "Idade média",
    f"{idade_alto:.1f} anos"
)

c3.metric(
    "Renda média",
    f"R$ {renda_alto:,.2f}"
)

st.markdown(
    f"""
    ### 🎯 Recomendação de Marketing

    O grupo com **Fancy Score >= 50%** apresenta maior afinidade
    com produtos Fancy e maior lucro médio por compra.

    Esse grupo representa aproximadamente **{percentual_alto:.1f}%**
    dos clientes.

    A recomendação é utilizar o Fancy Score para segmentação e
    direcionar campanhas para clientes com maior propensão a comprar
    produtos Fancy.

    As estratégias podem incluir:

    - Upsell de produtos Fancy;
    - Cross-sell;
    - Campanhas personalizadas;
    - Segmentação por comportamento de compra;
    - Priorização dos canais com maior participação Fancy.
    """
)

st.divider()

st.header("5️⃣ Fancy por canal")

canal = (
    df.groupby("canal_aquisicao")
    .agg(
        compras=("id_pedido", "count"),
        compras_fancy=("is_fancy", "sum")
    )
    .reset_index()
)

canal["percentual_fancy"] = (
    canal["compras_fancy"]
    / canal["compras"]
    * 100
)

fig4 = px.bar(
    canal.sort_values(
        "percentual_fancy",
        ascending=False
    ),
    x="canal_aquisicao",
    y="percentual_fancy",
    text_auto=".1f",
    title="% de compras Fancy por canal",
    labels={
        "canal_aquisicao": "Canal",
        "percentual_fancy": "% Fancy"
    }
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.header("🧠 Conclusão")

st.success(
    f"""
    O Fancy Score apresentou correlação de **{correlacao:.3f}**
    com o lucro médio por compra.

    Clientes com Fancy Score >= 50% apresentaram lucro médio de
    **R$ {lucro_alto:.2f}**, contra **R$ {lucro_baixo:.2f}** dos
    clientes abaixo de 50%.

    A diferença observada foi de **{diferenca:.1f}%**.

    Portanto, os dados apresentam evidências de uma associação positiva
    entre maior afinidade por produtos Fancy e maior rentabilidade.

    O Marketing deve utilizar o Fancy Score para identificar e
    segmentar clientes com maior propensão à compra de produtos Fancy.
    """
)

st.caption("Estudo de Caso — Efeito Fancy")
