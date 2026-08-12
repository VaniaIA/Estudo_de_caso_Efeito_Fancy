import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Efeito Fancy",
    page_icon="✨",
    layout="wide"
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

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


# ============================================================
# TÍTULO
# ============================================================

st.title("✨ Efeito Fancy")

st.markdown(
    """
    ### Fancy Score, Efeito Fancy e público-alvo

    Este dashboard analisa a participação de produtos Fancy nas compras
    dos clientes e sua relação com o lucro.
    """
)


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros")


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


if df_filtrado.empty:

    st.warning("Nenhum dado encontrado com os filtros selecionados.")

    st.stop()


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

percentual_fancy = df_filtrado["is_fancy"].mean() * 100


st.header("📊 Visão geral")


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Clientes",
    f"{total_clientes:,}".replace(",", ".")
)


c2.metric(
    "Compras",
    f"{total_compras:,}".replace(",", ".")
)


c3.metric(
    "Fancy Score médio",
    f"{fancy_score_medio:.2f}%"
)


c4.metric(
    "Compras Fancy",
    f"{percentual_fancy:.2f}%"
)


st.divider()


# ============================================================
# 1. FANCY SCORE
# ============================================================

st.header("1️⃣ Fancy Score por cliente")


st.markdown(
    """
    O Fancy Score representa a porcentagem das compras de cada cliente
    que pertence à linha Fancy.

    **Fancy Score = (Compras Fancy ÷ Total de Compras) × 100**
    """
)


fig_score = px.histogram(
    clientes,
    x="fancy_score",
    nbins=20,
    title="Distribuição do Fancy Score",
    labels={
        "fancy_score": "Fancy Score (%)",
        "count": "Quantidade de clientes"
    }
)


st.plotly_chart(
    fig_score,
    use_container_width=True
)


# ============================================================
# 2. EFEITO FANCY
# ============================================================

st.header("2️⃣ Efeito Fancy")


st.markdown(
    """
    O objetivo é verificar se clientes que compram uma proporção maior
    de produtos Fancy apresentam maior lucro médio por compra.
    """
)


# IMPORTANTE:
# Não usamos trendline="ols".
# Portanto, não precisamos de statsmodels.

correlacao = clientes["fancy_score"].corr(
    clientes["lucro_medio_compra"]
)


fig_scatter = px.scatter(
    clientes,
    x="fancy_score",
    y="lucro_medio_compra",
    title="Fancy Score x Lucro Médio por Compra",
    labels={
        "fancy_score": "Fancy Score (%)",
        "lucro_medio_compra": "Lucro médio por compra (R$)",
        "id_cliente": "Cliente",
        "total_compras": "Total de compras",
        "idade": "Idade",
        "renda_mensal": "Renda mensal"
    },
    hover_data=[
        "id_cliente",
        "total_compras",
        "idade",
        "renda_mensal"
    ]
)


st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# ============================================================
# CORRELAÇÃO
# ============================================================

st.subheader("📐 Evidência matemática")


c1, c2 = st.columns(2)


c1.metric(
    "Correlação de Pearson",
    f"{correlacao:.3f}"
)


if correlacao >= 0.7:

    c2.success(
        "Existe uma relação positiva forte."
    )

elif correlacao >= 0.3:

    c2.info(
        "Existe uma relação positiva moderada."
    )

elif correlacao >= -0.3:

    c2.warning(
        "Existe uma relação linear fraca."
    )

else:

    c2.error(
        "Existe uma relação negativa."
    )


st.markdown(
    f"""
    A correlação encontrada foi de **{correlacao:.3f}**.

    Esse resultado indica uma relação positiva entre o Fancy Score e o
    lucro médio por compra.

    Portanto, nos dados analisados, clientes com maior participação de
    produtos Fancy tendem a apresentar maior lucro médio.

    **Observação:** correlação demonstra associação estatística e não
    prova, sozinha, uma relação de causa e efeito.
    """
)


st.divider()


# ============================================================
# 3. COMPARAÇÃO DOS GRUPOS
# ============================================================

st.header("3️⃣ Comparação entre clientes")


grupo_baixo = clientes[
    clientes["fancy_score"] < 50
]


grupo_alto = clientes[
    clientes["fancy_score"] >= 50
]


lucro_baixo = grupo_baixo[
    "lucro_medio_compra"
].mean()


lucro_alto = grupo_alto[
    "lucro_medio_compra"
].mean()


if lucro_baixo != 0:

    diferenca = (
        (lucro_alto - lucro_baixo)
        / lucro_baixo
        * 100
    )

else:

    diferenca = 0


comparacao = pd.DataFrame(
    {
        "Grupo": [
            "Fancy Score < 50%",
            "Fancy Score >= 50%"
        ],
        "Lucro médio": [
            lucro_baixo,
            lucro_alto
        ]
    }
)


fig_grupos = px.bar(
    comparacao,
    x="Grupo",
    y="Lucro médio",
    text_auto=".2f",
    title="Lucro médio por compra por grupo",
    labels={
        "Grupo": "Grupo de clientes",
        "Lucro médio": "Lucro médio por compra (R$)"
    }
)


st.plotly_chart(
    fig_grupos,
    use_container_width=True
)


c1, c2, c3 = st.columns(3)


c1.metric(
    "Fancy Score < 50%",
    f"R$ {lucro_baixo:.2f}"
)


c2.metric(
    "Fancy Score >= 50%",
    f"R$ {lucro_alto:.2f}"
)


c3.metric(
    "Diferença",
    f"{diferenca:.1f}%"
)


st.markdown(
    f"""
    Clientes com Fancy Score >= 50% apresentam lucro médio de
    **R$ {lucro_alto:.2f}** por compra.

    Clientes com Fancy Score < 50% apresentam lucro médio de
    **R$ {lucro_baixo:.2f}** por compra.

    A diferença entre os grupos é de aproximadamente
    **{diferenca:.1f}%**.
    """
)


st.divider()


# ============================================================
# 4. CANAIS DE AQUISIÇÃO
# ============================================================

st.header("4️⃣ Participação Fancy por canal")


canal = (
    df_filtrado
    .groupby("canal_aquisicao")
    .agg(
        total_compras=("id_pedido", "count"),
        compras_fancy=("is_fancy", "sum"),
        lucro_medio=("Lucro Bruto", "mean")
    )
    .reset_index()
)


canal["percentual_fancy"] = (
    canal["compras_fancy"]
    / canal["total_compras"]
    * 100
)


canal = canal.sort_values(
    "percentual_fancy",
    ascending=False
)


fig_canal = px.bar(
    canal,
    x="canal_aquisicao",
    y="percentual_fancy",
    text_auto=".1f",
    title="Percentual de compras Fancy por canal",
    labels={
        "canal_aquisicao": "Canal de aquisição",
        "percentual_fancy": "% de compras Fancy"
    }
)


st.plotly_chart(
    fig_canal,
    use_container_width=True
)


st.dataframe(
    canal,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# 5. FANCY SCORE POR IDADE
# ============================================================

st.header("5️⃣ Fancy Score por faixa etária")


clientes["faixa_etaria"] = pd.cut(
    clientes["idade"],
    bins=[
        17,
        25,
        35,
        45,
        55,
        70
    ],
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
    .groupby(
        "faixa_etaria",
        observed=False
    )
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


st.divider()


# ============================================================
# 6. PÚBLICO-ALVO
# ============================================================

st.header("6️⃣ Público-alvo recomendado")


percentual_clientes_alto = (
    len(grupo_alto)
    /
    len(clientes)
    *
    100
)


idade_media_alto = grupo_alto["idade"].mean()

renda_media_alto = grupo_alto["renda_mensal"].mean()


c1, c2, c3 = st.columns(3)


c1.metric(
    "Clientes >= 50% Fancy",
    f"{percentual_clientes_alto:.1f}%"
)


c2.metric(
    "Idade média",
    f"{idade_media_alto:.1f} anos"
)


c3.metric(
    "Renda média",
    f"R$ {renda_media_alto:,.2f}"
)


st.markdown(
    f"""
    ### 🎯 Recomendação de Marketing

    O público prioritário deve ser formado por clientes que apresentam
    maior afinidade com produtos Fancy.

    O grupo com **Fancy Score >= 50% representa {percentual_clientes_alto:.1f}%**
    dos clientes analisados.

    Esse público apresentou lucro médio por compra de
    **R$ {lucro_alto:.2f}**, superior ao grupo com Fancy Score abaixo
    de 50%.

    Recomenda-se:

    - utilizar o Fancy Score para segmentação;
    - criar campanhas específicas para produtos Fancy;
    - trabalhar upsell e cross-sell;
    - priorizar canais com maior participação Fancy;
    - testar campanhas personalizadas para clientes de maior afinidade.
    """
)


st.divider()


# ============================================================
# 7. CONCLUSÃO
# ============================================================

st.header("🧠 Conclusão")


st.success(
    f"""
    ### Resultado do estudo

    O Fancy Score permitiu medir a participação dos produtos Fancy nas
    compras de cada cliente.

    A correlação entre Fancy Score e lucro médio por compra foi de
    **{correlacao:.3f}**, indicando uma relação positiva.

    Clientes com Fancy Score >= 50% apresentaram lucro médio de
    **R$ {lucro_alto:.2f}** por compra.

    Clientes com Fancy Score < 50% apresentaram lucro médio de
    **R$ {lucro_baixo:.2f}** por compra.

    A diferença observada entre os grupos foi de
    **{diferenca:.1f}%**.

    Portanto, os dados fornecem evidências de uma associação positiva
    entre maior afinidade por produtos Fancy e maior rentabilidade.

    **Recomendação:** utilizar o Fancy Score como indicador para
    segmentar clientes e direcionar futuras campanhas de Marketing.
    """
)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Estudo de Caso — Efeito Fancy"
)
```
