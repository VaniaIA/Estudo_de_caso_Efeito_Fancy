import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Efeito Fancy - Dashboard",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Efeito Fancy")
st.markdown(
    """
    **Análise do comportamento dos clientes e impacto dos produtos Fancy
    na rentabilidade.**
    """
)

# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados():
    df = pd.read_csv("vendas_clientes_catalogo.csv")

    # Identifica se a compra pertence à linha Fancy
    df["is_fancy"] = (
        df["linha"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("fancy")
    )

    return df


df = carregar_dados()

# ============================================================
# SIDEBAR - FILTROS
# ============================================================

st.sidebar.header("Filtros")

estados = st.sidebar.multiselect(
    "Estado",
    sorted(df["estado"].dropna().unique()),
    default=sorted(df["estado"].dropna().unique())
)

canais = st.sidebar.multiselect(
    "Canal de aquisição",
    sorted(df["canal_aquisicao"].dropna().unique()),
    default=sorted(df["canal_aquisicao"].dropna().unique())
)

categorias = st.sidebar.multiselect(
    "Categoria",
    sorted(df["categoria"].dropna().unique()),
    default=sorted(df["categoria"].dropna().unique())
)

df_filtrado = df[
    df["estado"].isin(estados)
    & df["canal_aquisicao"].isin(canais)
    & df["categoria"].isin(categorias)
].copy()

# ============================================================
# FANCY SCORE POR CLIENTE
# ============================================================

clientes = (
    df_filtrado
    .groupby("id_cliente")
    .agg(
        total_compras=("id_pedido", "count"),
        compras_fancy=("is_fancy", "sum"),
        lucro_total=("Lucro Bruto", "sum"),
        idade=("idade", "first"),
        renda_mensal=("renda_mensal", "first"),
        estado=("estado", "first"),
        canal_aquisicao=("canal_aquisicao", "first")
    )
    .reset_index()
)

clientes["fancy_score"] = (
    clientes["compras_fancy"]
    / clientes["total_compras"]
    * 100
)

clientes["lucro_medio_compra"] = (
    clientes["lucro_total"]
    / clientes["total_compras"]
)

# ============================================================
# KPIs
# ============================================================

total_clientes = clientes["id_cliente"].nunique()
total_compras = len(df_filtrado)

fancy_score_medio = clientes["fancy_score"].mean()

lucro_medio = df_filtrado["Lucro Bruto"].mean()

percentual_fancy = df_filtrado["is_fancy"].mean() * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Clientes",
    f"{total_clientes:,}".replace(",", ".")
)

col2.metric(
    "Compras",
    f"{total_compras:,}".replace(",", ".")
)

col3.metric(
    "Fancy Score médio",
    f"{fancy_score_medio:.2f}%"
)

col4.metric(
    "% de compras Fancy",
    f"{percentual_fancy:.2f}%"
)

st.divider()

# ============================================================
# GRÁFICO 1 - DISTRIBUIÇÃO DO FANCY SCORE
# ============================================================

st.subheader("📊 Fancy Score por cliente")

fig_score = px.histogram(
    clientes,
    x="fancy_score",
    nbins=20,
    labels={
        "fancy_score": "Fancy Score (%)",
        "count": "Quantidade de clientes"
    },
    title="Distribuição do Fancy Score"
)

fig_score.update_layout(
    xaxis_title="Fancy Score (%)",
    yaxis_title="Quantidade de clientes"
)

st.plotly_chart(fig_score, use_container_width=True)

st.info(
    """
    **Fancy Score** representa a porcentagem das compras de cada cliente
    que pertence à linha Fancy.
    """
)

# ============================================================
# SEGMENTAÇÃO DOS CLIENTES
# ============================================================

def classificar_fancy(score):

    if score == 0:
        return "0% Fancy"

    elif score <= 25:
        return "1–25% Fancy"

    elif score <= 50:
        return "26–50% Fancy"

    elif score <= 75:
        return "51–75% Fancy"

    else:
        return "76–100% Fancy"


clientes["faixa_fancy"] = clientes["fancy_score"].apply(
    classificar_fancy
)

# ============================================================
# GRÁFICO 2 - FANCY SCORE X LUCRO
# ============================================================

st.subheader("💰 Efeito Fancy: Fancy Score x Lucro")

fig_scatter = px.scatter(
    clientes,
    x="fancy_score",
    y="lucro_medio_compra",
    trendline="ols",
    hover_data=[
        "id_cliente",
        "total_compras",
        "idade",
        "renda_mensal"
    ],
    labels={
        "fancy_score": "Fancy Score (%)",
        "lucro_medio_compra": "Lucro médio por compra (R$)"
    },
    title="Quanto maior o Fancy Score, maior tende a ser o lucro"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================
# CORRELAÇÃO
# ============================================================

correlacao = clientes[
    ["fancy_score", "lucro_medio_compra"]
].corr().iloc[0, 1]

st.metric(
    "Correlação entre Fancy Score e lucro médio",
    f"{correlacao:.3f}"
)

st.markdown(
    f"""
    **Interpretação:** a correlação de **{correlacao:.3f}** indica uma
    relação positiva forte entre a participação de produtos Fancy nas
    compras do cliente e seu lucro médio por compra.
    """
)

# ============================================================
# COMPARAÇÃO < 50% X >= 50%
# ============================================================

st.subheader("📈 Comparação entre clientes")

clientes_baixo = clientes[
    clientes["fancy_score"] < 50
]

clientes_alto = clientes[
    clientes["fancy_score"] >= 50
]

lucro_baixo = clientes_baixo["lucro_medio_compra"].mean()
lucro_alto = clientes_alto["lucro_medio_compra"].mean()

uplift = (
    (lucro_alto - lucro_baixo)
    / lucro_baixo
    * 100
)

comparacao = pd.DataFrame({
    "Grupo": [
        "Fancy Score < 50%",
        "Fancy Score ≥ 50%"
    ],
    "Lucro médio por compra": [
        lucro_baixo,
        lucro_alto
    ]
})

fig_comparacao = px.bar(
    comparacao,
    x="Grupo",
    y="Lucro médio por compra",
    text_auto=".2f",
    title="Lucro médio por compra por grupo"
)

st.plotly_chart(
    fig_comparacao,
    use_container_width=True
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Lucro médio < 50%",
    f"R$ {lucro_baixo:.2f}"
)

c2.metric(
    "Lucro médio ≥ 50%",
    f"R$ {lucro_alto:.2f}"
)

c3.metric(
    "Diferença",
    f"+{uplift:.1f}%"
)

# ============================================================
# PERFIL DO PÚBLICO-ALVO
# ============================================================

st.divider()

st.subheader("🎯 Público-alvo recomendado")

st.markdown(
    """
    ### Público prioritário

    O grupo de clientes com **Fancy Score ≥ 50%** apresenta maior
    rentabilidade média e maior afinidade com produtos Fancy.

    A recomendação é priorizar:

    - Clientes com maior propensão a comprar produtos Fancy;
    - Público mais jovem;
    - Campanhas nos canais **TikTok** e **Instagram**;
    - Estratégias de upsell e cross-sell de produtos Fancy.
    """
)

# ============================================================
# ANÁLISE POR CANAL
# ============================================================

canal = (
    df_filtrado
    .groupby("canal_aquisicao")
    .agg(
        compras=("id_pedido", "count"),
        percentual_fancy=("is_fancy", "mean"),
        lucro_medio=("Lucro Bruto", "mean")
    )
    .reset_index()
)

canal["percentual_fancy"] *= 100

fig_canal = px.bar(
    canal.sort_values("percentual_fancy", ascending=False),
    x="canal_aquisicao",
    y="percentual_fancy",
    text_auto=".1f",
    title="% de compras Fancy por canal",
    labels={
        "canal_aquisicao": "Canal",
        "percentual_fancy": "% de compras Fancy"
    }
)

st.plotly_chart(
    fig_canal,
    use_container_width=True
)

# ============================================================
# ANÁLISE POR IDADE
# ============================================================

clientes["faixa_etaria"] = pd.cut(
    clientes["idade"],
    bins=[17, 25, 35, 45, 55, 70],
    labels=[
        "18–25",
        "26–35",
        "36–45",
        "46–55",
        "56–69"
    ]
)

idade = (
    clientes
    .groupby("faixa_etaria", observed=False)
    .agg(
        fancy_score_medio=("fancy_score", "mean"),
        lucro_medio=("lucro_medio_compra", "mean"),
        clientes=("id_cliente", "count")
    )
    .reset_index()
)

fig_idade = px.bar(
    idade,
    x="faixa_etaria",
    y="fancy_score_medio",
    text_auto=".1f",
    title="Fancy Score médio por faixa etária",
    labels={
        "faixa_etaria": "Faixa etária",
        "fancy_score_medio": "Fancy Score médio (%)"
    }
)

st.plotly_chart(
    fig_idade,
    use_container_width=True
)

# ============================================================
# CONCLUSÃO
# ============================================================

st.divider()

st.subheader("🧠 Conclusão da análise")

st.success(
    f"""
    O Efeito Fancy é evidenciado pela relação positiva entre o Fancy Score
    e o lucro médio por compra. A correlação observada é de
    **{correlacao:.3f}**.

    Clientes com Fancy Score ≥ 50% apresentam lucro médio de
    **R$ {lucro_alto:.2f}**, contra **R$ {lucro_baixo:.2f}** para clientes
    com Fancy Score abaixo de 50%.

    Isso representa uma diferença de aproximadamente
    **{uplift:.1f}%** no lucro médio por compra.

    Portanto, a estratégia recomendada é direcionar campanhas para
    públicos com maior propensão a produtos Fancy, especialmente através
    dos canais de maior afinidade com essa linha.
    """
)
