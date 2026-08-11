```python
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# ============================================================
# CONFIGURAÇÃO DO DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Efeito Fancy - Dashboard",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Efeito Fancy")
st.markdown(
    """
    ### Análise do comportamento dos clientes e impacto dos produtos Fancy

    Este dashboard calcula o **Fancy Score** de cada cliente e analisa
    sua relação com o lucro médio por compra, buscando identificar
    evidências do **Efeito Fancy** e apoiar decisões de Marketing.
    """
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados():

    df = pd.read_csv("vendas_clientes_catalogo.csv")

    # Identifica compras da linha Fancy
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

st.sidebar.header("🔎 Filtros")

estados_disponiveis = sorted(
    df["estado"].dropna().unique()
)

canais_disponiveis = sorted(
    df["canal_aquisicao"].dropna().unique()
)

categorias_disponiveis = sorted(
    df["categoria"].dropna().unique()
)


estados = st.sidebar.multiselect(
    "Estado",
    estados_disponiveis,
    default=estados_disponiveis
)


canais = st.sidebar.multiselect(
    "Canal de aquisição",
    canais_disponiveis,
    default=canais_disponiveis
)


categorias = st.sidebar.multiselect(
    "Categoria",
    categorias_disponiveis,
    default=categorias_disponiveis
)


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

df_filtrado = df[
    df["estado"].isin(estados)
    & df["canal_aquisicao"].isin(canais)
    & df["categoria"].isin(categorias)
].copy()


# ============================================================
# VALIDAÇÃO DOS DADOS
# ============================================================

if df_filtrado.empty:

    st.warning(
        "Nenhum registro encontrado com os filtros selecionados."
    )

    st.stop()


# ============================================================
# CÁLCULO DO FANCY SCORE POR CLIENTE
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


# Fancy Score =
# quantidade de compras Fancy / total de compras * 100

clientes["fancy_score"] = (
    clientes["compras_fancy"]
    / clientes["total_compras"]
    * 100
)


# Lucro médio gerado por compra do cliente

clientes["lucro_medio_compra"] = (
    clientes["lucro_total"]
    / clientes["total_compras"]
)


# ============================================================
# KPIs PRINCIPAIS
# ============================================================

total_clientes = clientes["id_cliente"].nunique()

total_compras = len(df_filtrado)

fancy_score_medio = clientes["fancy_score"].mean()

percentual_fancy = (
    df_filtrado["is_fancy"].mean()
    * 100
)

lucro_medio = (
    df_filtrado["Lucro Bruto"].mean()
)


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "👥 Clientes",
    f"{total_clientes:,}".replace(",", ".")
)


col2.metric(
    "🛒 Compras",
    f"{total_compras:,}".replace(",", ".")
)


col3.metric(
    "✨ Fancy Score médio",
    f"{fancy_score_medio:.2f}%"
)


col4.metric(
    "📦 % de compras Fancy",
    f"{percentual_fancy:.2f}%"
)


st.divider()


# ============================================================
# SEÇÃO 1 - FANCY SCORE
# ============================================================

st.header("1️⃣ Fancy Score por Cliente")

st.markdown(
    """
    O **Fancy Score** representa a porcentagem das compras de cada
    cliente que pertence à linha Fancy.

    **Fórmula:**

    Fancy Score = (Compras Fancy ÷ Total de Compras) × 100
    """
)


# ============================================================
# HISTOGRAMA DO FANCY SCORE
# ============================================================

fig_score = px.histogram(
    clientes,
    x="fancy_score",
    nbins=20,
    labels={
        "fancy_score": "Fancy Score (%)",
        "count": "Quantidade de clientes"
    },
    title="Distribuição do Fancy Score entre os clientes"
)


fig_score.update_layout(
    xaxis_title="Fancy Score (%)",
    yaxis_title="Quantidade de clientes"
)


st.plotly_chart(
    fig_score,
    use_container_width=True
)


# ============================================================
# SEGMENTAÇÃO DOS CLIENTES POR FANCY SCORE
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


clientes["faixa_fancy"] = (
    clientes["fancy_score"]
    .apply(classificar_fancy)
)


# ============================================================
# TABELA DE DISTRIBUIÇÃO
# ============================================================

distribuicao = (
    clientes
    .groupby("faixa_fancy")
    .agg(
        clientes=("id_cliente", "count"),
        fancy_score_medio=("fancy_score", "mean"),
        lucro_medio=("lucro_medio_compra", "mean")
    )
    .reset_index()
)


ordem_faixas = [
    "0% Fancy",
    "1–25% Fancy",
    "26–50% Fancy",
    "51–75% Fancy",
    "76–100% Fancy"
]


distribuicao["faixa_fancy"] = pd.Categorical(
    distribuicao["faixa_fancy"],
    categories=ordem_faixas,
    ordered=True
)


distribuicao = distribuicao.sort_values(
    "faixa_fancy"
)


st.subheader("Distribuição dos clientes por faixa de Fancy Score")


st.dataframe(
    distribuicao,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SEÇÃO 2 - EFEITO FANCY
# ============================================================

st.header("2️⃣ Efeito Fancy")

st.markdown(
    """
    Para avaliar o Efeito Fancy, analisamos a relação entre o
    **Fancy Score do cliente** e seu **lucro médio por compra**.
    """
)


# ============================================================
# DADOS PARA O GRÁFICO
# ============================================================

dados_scatter = clientes[
    [
        "id_cliente",
        "fancy_score",
        "lucro_medio_compra",
        "total_compras",
        "idade",
        "renda_mensal"
    ]
].dropna()


# ============================================================
# CORRELAÇÃO DE PEARSON
# ============================================================

correlacao = dados_scatter[
    "fancy_score"
].corr(
    dados_scatter["lucro_medio_compra"]
)


# ============================================================
# REGRESSÃO LINEAR MANUAL
# ============================================================
#
# Utilizamos numpy para calcular a linha de tendência.
#
# Isso evita o uso de:
#
# trendline="ols"
#
# que exige a instalação do statsmodels.
# ============================================================

x = dados_scatter["fancy_score"].values

y = dados_scatter["lucro_medio_compra"].values


coeficiente_angular, intercepto = np.polyfit(
    x,
    y,
    1
)


dados_scatter["linha_tendencia"] = (
    coeficiente_angular
    * dados_scatter["fancy_score"]
    + intercepto
)


# ============================================================
# GRÁFICO DE DISPERSÃO
# ============================================================

fig_scatter = px.scatter(
    dados_scatter,
    x="fancy_score",
    y="lucro_medio_compra",
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
    title="Relação entre Fancy Score e Lucro Médio por Compra"
)


# Adiciona a linha de tendência manualmente

fig_scatter.add_scatter(
    x=dados_scatter["fancy_score"],
    y=dados_scatter["linha_tendencia"],
    mode="lines",
    name="Linha de tendência"
)


st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# ============================================================
# INDICADOR DE CORRELAÇÃO
# ============================================================

st.subheader("📐 Evidência matemática")


col_corr, col_interpretacao = st.columns([1, 2])


with col_corr:

    st.metric(
        "Correlação de Pearson",
        f"{correlacao:.3f}"
    )


with col_interpretacao:

    if correlacao >= 0.7:

        st.success(
            f"""
            A correlação de **{correlacao:.3f}** indica uma relação
            positiva forte entre o Fancy Score e o lucro médio por compra.
            """
        )

    elif correlacao >= 0.3:

        st.info(
            f"""
            A correlação de **{correlacao:.3f}** indica uma relação
            positiva moderada entre as variáveis.
            """
        )

    elif correlacao > -0.3:

        st.warning(
            f"""
            A correlação de **{correlacao:.3f}** indica uma relação
            linear fraca entre as variáveis.
            """
        )

    else:

        st.warning(
            f"""
            A correlação de **{correlacao:.3f}** indica uma relação
            negativa entre as variáveis.
            """
        )


st.markdown(
    """
    ### Como interpretar

    A correlação de Pearson varia de **-1 a +1**.

    - Próximo de **+1** → relação positiva forte
    - Próximo de **0** → relação linear fraca
    - Próximo de **-1** → relação negativa forte

    Portanto, uma correlação positiva elevada indica que clientes com
    maior participação de produtos Fancy tendem a apresentar maior
    lucro médio por compra.

    **Importante:** essa análise demonstra associação estatística,
    mas não permite afirmar, sozinha, que a compra de produtos Fancy
    causa o aumento do lucro.
    """
)


# ============================================================
# SEÇÃO 3 - COMPARAÇÃO ENTRE GRUPOS
# ============================================================

st.header("3️⃣ Comparação: clientes com maior afinidade Fancy")


clientes_baixo = clientes[
    clientes["fancy_score"] < 50
].copy()


clientes_alto = clientes[
    clientes["fancy_score"] >= 50
].copy()


lucro_baixo = (
    clientes_baixo["lucro_medio_compra"]
    .mean()
)


lucro_alto = (
    clientes_alto["lucro_medio_compra"]
    .mean()
)


# Calcula diferença percentual

if lucro_baixo != 0:

    uplift = (
        (lucro_alto - lucro_baixo)
        / lucro_baixo
        * 100
    )

else:

    uplift = 0


# ============================================================
# GRÁFICO COMPARATIVO
# ============================================================

comparacao = pd.DataFrame(
    {
        "Grupo": [
            "Fancy Score < 50%",
            "Fancy Score ≥ 50%"
        ],
        "Lucro médio por compra": [
            lucro_baixo,
            lucro_alto
        ]
    }
)


fig_comparacao = px.bar(
    comparacao,
    x="Grupo",
    y="Lucro médio por compra",
    text_auto=".2f",
    title="Lucro médio por compra por grupo",
    labels={
        "Grupo": "Grupo de clientes",
        "Lucro médio por compra":
            "Lucro médio por compra (R$)"
    }
)


st.plotly_chart(
    fig_comparacao,
    use_container_width=True
)


# ============================================================
# KPIs DA COMPARAÇÃO
# ============================================================

col1, col2, col3 = st.columns(3)


col1.metric(
    "Lucro médio < 50%",
    f"R$ {lucro_baixo:.2f}"
)


col2.metric(
    "Lucro médio ≥ 50%",
    f"R$ {lucro_alto:.2f}"
)


col3.metric(
    "Diferença",
    f"+{uplift:.1f}%"
)


st.markdown(
    f"""
    Clientes com **Fancy Score ≥ 50%** apresentam lucro médio de
    **R$ {lucro_alto:.2f} por compra**, enquanto clientes com Fancy
    Score abaixo de 50% apresentam lucro médio de
    **R$ {lucro_baixo:.2f}**.

    Isso representa uma diferença de aproximadamente
    **{uplift:.1f}%**.
    """
)


# ============================================================
# SEÇÃO 4 - PÚBLICO-ALVO
# ============================================================

st.divider()

st.header("4️⃣ Público-alvo recomendado para Marketing")


# ============================================================
# PERFIL DOS DOIS GRUPOS
# ============================================================

idade_baixo = clientes_baixo["idade"].mean()
idade_alto = clientes_alto["idade"].mean()

renda_baixo = clientes_baixo["renda_mensal"].mean()
renda_alto = clientes_alto["renda_mensal"].mean()

percentual_clientes_alto = (
    len(clientes_alto)
    / len(clientes)
    * 100
)


col1, col2, col3 = st.columns(3)


col1.metric(
    "Clientes com Fancy Score ≥ 50%",
    f"{percentual_clientes_alto:.1f}%"
)


col2.metric(
    "Idade média",
    f"{idade_alto:.1f} anos"
)


col3.metric(
    "Renda média",
    f"R$ {renda_alto:,.2f}".replace(
        ",", "X"
    ).replace(
        ".", ","
    ).replace(
        "X", "."
    )
)


st.markdown(
    f"""
    ### 🎯 Recomendação

    O grupo de clientes com **Fancy Score ≥ 50%** apresenta maior
    afinidade com produtos Fancy e maior lucro médio por compra.

    **Características do grupo:**

    - Fancy Score igual ou superior a 50%;
    - Idade média de aproximadamente **{idade_alto:.1f} anos**;
    - Renda mensal média de aproximadamente **R$ {renda_alto:,.2f}**;
    - Maior rentabilidade média por compra.

    **Estratégia recomendada:**

    1. Identificar clientes com maior probabilidade de comprar produtos
       Fancy;
    2. Criar campanhas específicas para esse público;
    3. Utilizar produtos Fancy em estratégias de upsell e cross-sell;
    4. Priorizar os canais que apresentam maior participação de compras
       Fancy.
    """
)


# ============================================================
# SEÇÃO 5 - ANÁLISE POR CANAL
# ============================================================

st.header("5️⃣ Fancy Score por canal de aquisição")


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


canal = canal.sort_values(
    "percentual_fancy",
    ascending=False
)


# ============================================================
# GRÁFICO POR CANAL
# ============================================================

fig_canal = px.bar(
    canal,
    x="canal_aquisicao",
    y="percentual_fancy",
    text_auto=".1f",
    title="% de compras Fancy por canal",
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


# ============================================================
# SEÇÃO 6 - FANCY SCORE POR IDADE
# ============================================================

st.header("6️⃣ Fancy Score por faixa etária")


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


# ============================================================
# GRÁFICO POR IDADE
# ============================================================

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

st.header("🧠 Conclusão da análise")


st.success(
    f"""
    ### Resultado do estudo

    O **Efeito Fancy** apresenta evidências estatísticas nos dados
    analisados.

    O Fancy Score foi calculado individualmente para cada cliente,
    representando a porcentagem de suas compras que pertence à linha
    Fancy.

    A correlação entre Fancy Score e lucro médio por compra foi de
    **{correlacao:.3f}**, indicando uma relação positiva entre essas
    duas variáveis.

    Além disso, clientes com Fancy Score ≥ 50% apresentaram lucro médio
    de **R$ {lucro_alto:.2f} por compra**, enquanto clientes com
    Fancy Score < 50% apresentaram **R$ {lucro_baixo:.2f}**.

    A diferença entre os grupos foi de aproximadamente
    **{uplift:.1f}%**.

    ### Recomendação para Marketing

    A empresa deve priorizar clientes com maior propensão a comprar
    produtos Fancy, utilizando campanhas segmentadas e estratégias
    de upsell e cross-sell.

    Os canais com maior participação de compras Fancy devem receber
    atenção especial nas próximas campanhas.

    **Observação:** os resultados demonstram associação estatística
    entre Fancy Score e rentabilidade. Isso não significa,
    necessariamente, que a compra de produtos Fancy seja a causa
    direta do aumento do lucro.
    """
)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Dashboard desenvolvido para o estudo de caso — Efeito Fancy"
)
```
