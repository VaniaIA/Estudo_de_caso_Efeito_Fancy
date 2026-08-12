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
# TÍTULO
# ============================================================

st.title("✨ Efeito Fancy")

st.markdown(
    """
    **Análise do comportamento dos clientes, Fancy Score e
    rentabilidade para apoio às decisões de Marketing.**
    """
)


# ============================================================
# CARREGAR DADOS
# ============================================================

@st.cache_data
def carregar_dados():

    dados = pd.read_csv("vendas_clientes_catalogo.csv")

    # Identifica se a compra pertence à linha Fancy
    dados["is_fancy"] = (
        dados["linha"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "fancy"
    )

    return dados


df = carregar_dados()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔎 Filtros")


# Estados
lista_estados = sorted(
    df["estado"].dropna().unique().tolist()
)

estados = st.sidebar.multiselect(
    "Estado",
    lista_estados,
    default=lista_estados
)


# Canais
lista_canais = sorted(
    df["canal_aquisicao"].dropna().unique().tolist()
)

canais = st.sidebar.multiselect(
    "Canal de aquisição",
    lista_canais,
    default=lista_canais
)


# Categorias
lista_categorias = sorted(
    df["categoria"].dropna().unique().tolist()
)

categorias = st.sidebar.multiselect(
    "Categoria",
    lista_categorias,
    default=lista_categorias
)


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df[
    df["estado"].isin(estados)
    &
    df["canal_aquisicao"].isin(canais)
    &
    df["categoria"].isin(categorias)
].copy()


# ============================================================
# VERIFICAR SE EXISTEM DADOS
# ============================================================

if df_filtrado.empty:

    st.warning(
        "Nenhum dado foi encontrado com os filtros selecionados."
    )

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


# ============================================================
# CÁLCULO DO FANCY SCORE
# ============================================================

clientes["fancy_score"] = (
    clientes["compras_fancy"]
    /
    clientes["total_compras"]
    *
    100
)


# ============================================================
# LUCRO MÉDIO POR COMPRA
# ============================================================

clientes["lucro_medio_compra"] = (
    clientes["lucro_total"]
    /
    clientes["total_compras"]
)


# ============================================================
# ============================================================
# PAINEL PRINCIPAL - KPIs
# ============================================================
# ============================================================

st.header("📊 Visão geral")


total_clientes = clientes["id_cliente"].nunique()

total_compras = len(df_filtrado)

fancy_score_medio = clientes["fancy_score"].mean()

percentual_fancy = (
    df_filtrado["is_fancy"].mean()
    *
    100
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "👥 Clientes",
        f"{total_clientes:,}".replace(",", ".")
    )


with col2:

    st.metric(
        "🛒 Compras",
        f"{total_compras:,}".replace(",", ".")
    )


with col3:

    st.metric(
        "✨ Fancy Score médio",
        f"{fancy_score_medio:.2f}%"
    )


with col4:

    st.metric(
        "📦 Compras Fancy",
        f"{percentual_fancy:.2f}%"
    )


st.divider()


# ============================================================
# ============================================================
# 1 - FANCY SCORE
# ============================================================
# ============================================================

st.header("1️⃣ Fancy Score por cliente")


st.markdown(
    """
    O **Fancy Score** mede qual porcentagem das compras de cada cliente
    pertence à linha Fancy.

    **Fórmula:**

    **Fancy Score = (Compras Fancy ÷ Total de Compras) × 100**
    """
)


# ============================================================
# HISTOGRAMA
# ============================================================

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


fig_score.update_layout(
    xaxis_title="Fancy Score (%)",
    yaxis_title="Quantidade de clientes"
)


st.plotly_chart(
    fig_score,
    use_container_width=True
)


# ============================================================
# TABELA POR FAIXA
# ============================================================

def classificar_fancy(score):

    if score == 0:
        return "0% Fancy"

    elif score <= 25:
        return "1% a 25%"

    elif score <= 50:
        return "26% a 50%"

    elif score <= 75:
        return "51% a 75%"

    else:
        return "76% a 100%"


clientes["faixa_fancy"] = (
    clientes["fancy_score"]
    .apply(classificar_fancy)
)


ordem_faixas = [
    "0% Fancy",
    "1% a 25%",
    "26% a 50%",
    "51% a 75%",
    "76% a 100%"
]


distribuicao = (
    clientes
    .groupby("faixa_fancy")
    .agg(
        quantidade_clientes=("id_cliente", "count"),
        fancy_score_medio=("fancy_score", "mean"),
        lucro_medio=("lucro_medio_compra", "mean")
    )
    .reset_index()
)


distribuicao["ordem"] = (
    distribuicao["faixa_fancy"]
    .map(
        {
            "0% Fancy": 1,
            "1% a 25%": 2,
            "26% a 50%": 3,
            "51% a 75%": 4,
            "76% a 100%": 5
        }
    )
)


distribuicao = (
    distribuicao
    .sort_values("ordem")
    .drop(columns="ordem")
)


st.subheader("Clientes por faixa de Fancy Score")


st.dataframe(
    distribuicao,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# ============================================================
# 2 - EFEITO FANCY
# ============================================================
# ============================================================

st.header("2️⃣ Efeito Fancy")


st.markdown(
    """
    Agora vamos verificar se existe uma relação entre a participação
    de produtos Fancy nas compras do cliente e o lucro médio gerado.
    """
)


# ============================================================
# CORRELAÇÃO
# ============================================================

correlacao = clientes[
    "fancy_score"
].corr(
    clientes["lucro_medio_compra"]
)


# ============================================================
# GRÁFICO DE DISPERSÃO
# ============================================================
#
# IMPORTANTE:
#
# NÃO usamos:
#
# trendline="ols"
#
# porque isso exige statsmodels.
#
# Portanto, este gráfico funciona somente com Plotly.
# ============================================================

fig_scatter = px.scatter(
    clientes,
    x="fancy_score",
    y="lucro_medio_compra",
    hover_data=[
        "id_cliente",
        "total_compras",
        "idade",
        "renda_mensal"
    ],
    title="Fancy Score x Lucro Médio por Compra",
    labels={
        "fancy_score": "Fancy Score (%)",
        "lucro_medio_compra": "Lucro médio por compra (R$)",
        "id_cliente": "Cliente",
        "total_compras": "Total de compras",
        "idade": "Idade",
        "renda_mensal": "Renda mensal"
    }
)


st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# ============================================================
# RESULTADO MATEMÁTICO
# ============================================================

st.subheader("📐 Evidência matemática do Efeito Fancy")


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Correlação de Pearson",
        f"{correlacao:.3f}"
    )


with col2:

    if correlacao >= 0.7:

        st.success(
            "Relação positiva forte"
        )

    elif correlacao >= 0.3:

        st.info(
            "Relação positiva moderada"
        )

    elif correlacao >= -0.3:

        st.warning(
            "Relação linear fraca"
        )

    else:

        st.error(
            "Relação negativa"
        )


st.markdown(
    f"""
    ### Interpretação

    O coeficiente de correlação encontrado foi de **{correlacao:.3f}**.

    Esse resultado indica que existe uma **relação positiva** entre o
    Fancy Score e o lucro médio por compra.

    Em outras palavras, nos dados analisados, clientes que apresentam
    maior participação de produtos Fancy em suas compras tendem a
    apresentar maior lucro médio por compra.

    **Importante:** correlação demonstra associação entre as variáveis.
    Ela não permite afirmar, sozinha, que comprar produtos Fancy seja
    a causa direta do aumento do lucro.
    """
)


st.divider()


# ============================================================
# ============================================================
# 3 - COMPARAÇÃO ENTRE CLIENTES
# ============================================================
# ============================================================

st.header("3️⃣ Comparação entre clientes")


clientes_baixo = clientes[
    clientes["fancy_score"] < 50
].copy()


clientes_alto = clientes[
    clientes["fancy_score"] >= 50
].copy()


# ============================================================
# LUCRO MÉDIO DOS GRUPOS
# ============================================================

lucro_baixo = (
    clientes_baixo["lucro_medio_compra"]
    .mean()
)


lucro_alto = (
    clientes_alto["lucro_medio_compra"]
    .mean()
)


# ============================================================
# DIFERENÇA PERCENTUAL
# ============================================================

if lucro_baixo != 0:

    diferenca_percentual = (
        (lucro_alto - lucro_baixo)
        /
        lucro_baixo
        *
        100
    )

else:

    diferenca_percentual = 0


# ============================================================
# GRÁFICO
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
    title="Lucro médio por compra segundo o Fancy Score",
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
# KPIs
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Fancy Score < 50%",
        f"R$ {lucro_baixo:.2f}"
    )


with col2:

    st.metric(
        "Fancy Score ≥ 50%",
        f"R$ {lucro_alto:.2f}"
    )


with col3:

    st.metric(
        "Diferença",
        f"{diferenca_percentual:.1f}%"
    )


st.markdown(
    f"""
    Clientes com **Fancy Score igual ou superior a 50%** apresentam
    lucro médio de **R$ {lucro_alto:.2f} por compra**.

    Já os clientes com Fancy Score abaixo de 50% apresentam lucro médio
    de **R$ {lucro_baixo:.2f} por compra**.

    A diferença entre os grupos é de aproximadamente
    **{diferenca_percentual:.1f}%**.
    """
)


st.divider()


# ============================================================
# ============================================================
# 4 - PERFIL DO PÚBLICO-ALVO
# ============================================================
# ============================================================

st.header("4️⃣ Público-alvo recomendado")


# ============================================================
# MÉTRICAS DO GRUPO FANCY ≥ 50%
# ============================================================

quantidade_alto = len(clientes_alto)

percentual_alto = (
    quantidade_alto
    /
    len(clientes)
    *
    100
)


idade_alto = clientes_alto["idade"].mean()

renda_alto = clientes_alto["renda_mensal"].mean()


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Clientes com Fancy Score ≥ 50%",
        f"{percentual_alto:.1f}%"
    )


with col2:

    st.metric(
        "Idade média",
        f"{idade_alto:.1f} anos"
    )


with col3:

    st.metric(
        "Renda média",
        f"R$ {renda_alto:,.2f}"
    )


st.markdown(
    f"""
    ### 🎯 Recomendação para Marketing

    Com base nos resultados, o grupo prioritário deve ser formado por
    clientes que apresentam **maior afinidade com produtos Fancy**.

    Esse grupo representa aproximadamente **{percentual_alto:.1f}%**
    dos clientes analisados.

    A estratégia recomendada é:

    **1.** Identificar clientes com maior Fancy Score.

    **2.** Criar campanhas específicas para produtos Fancy.

    **3.** Utilizar estratégias de **upsell** e **cross-sell**.

    **4.** Priorizar canais de aquisição que apresentam maior
    participação de produtos Fancy.

    **5.** Utilizar o Fancy Score como variável de segmentação para
    campanhas futuras.
    """
)


st.divider()


# ============================================================
# ============================================================
# 5 - ANÁLISE POR CANAL
# ============================================================
# ============================================================

st.header("5️⃣ Participação de produtos Fancy por canal")


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
    /
    canal["total_compras"]
    *
    100
)


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


st.divider()


# ============================================================
# ============================================================
# 6 - FANCY SCORE POR FAIXA ETÁRIA
# ============================================================
# ============================================================

st.header("6️⃣ Fancy Score por faixa etária")


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
# ============================================================
# 7 - CONCLUSÃO
# ============================================================
# ============================================================

st.divider()

st.header("🧠 Conclusão do estudo")


st.success(
    f"""
    ### Resultado

    O Fancy Score permite medir a participação dos produtos Fancy nas
    compras de cada cliente.

    A análise encontrou uma correlação de **{correlacao:.3f}** entre
    Fancy Score e lucro médio por compra, indicando uma relação
    positiva entre as duas variáveis.

    Além disso:

    **Clientes com Fancy Score < 50%:**
    R$ {lucro_baixo:.2f} de lucro médio por compra.

    **Clientes com Fancy Score ≥ 50%:**
    R$ {lucro_alto:.2f} de lucro médio por compra.

    **Diferença observada: {diferenca_percentual:.1f}%**

    ### Recomendação

    O Marketing deve utilizar o Fancy Score para identificar clientes
    com maior afinidade com produtos Fancy e direcionar campanhas
    segmentadas para esse público.

    Produtos Fancy podem ser utilizados em estratégias de upsell,
    cross-sell e campanhas personalizadas.

    **Observação:** os resultados demonstram associação estatística,
    e não necessariamente causalidade.
    """
)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Estudo de Caso — Efeito Fancy | Dashboard desenvolvido em Streamlit"
)
```
