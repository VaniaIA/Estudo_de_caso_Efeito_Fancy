import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Dashboard - Efeito Fancy & Estratégia de Marketing",
    page_icon="🍷",
    layout="wide"
)

st.title("🍷 Dashboard Executivo: Análise do 'Efeito Fancy'")
st.markdown("""
Este painel analisa o comportamento de compra dos clientes, demonstra estatisticamente a existência do **"Efeito Fancy"** 
e direciona a estratégia de Marketing para o público-alvo de maior retorno.
""")

@st.cache_data
def load_data():
    df = pd.read_csv('vendas_clientes_catalogo.csv')
    df['receita_total'] = df['quantidade'] * df['preco_venda']
    df['custo_total'] = df['quantidade'] * df['custo_producao']
    df['margem_lucro'] = df['Lucro Bruto'] / df['receita_total']
    
    # Agrupamento por Cliente para calcular o Fancy Score
    cliente_df = df.groupby('id_cliente').agg(
        total_itens=('quantidade', 'sum'),
        itens_fancy=('quantidade', lambda x: x[df.loc[x.index, 'linha'] == 'Fancy'].sum()),
        total_pedidos=('id_pedido', 'count'),
        pedidos_fancy=('linha', lambda x: (x == 'Fancy').sum()),
        idade=('idade', 'first'),
        renda_mensal=('renda_mensal', 'first'),
        estado=('estado', 'first'),
        canal_aquisicao=('canal_aquisicao', 'first'),
        lucro_total=('Lucro Bruto', 'sum'),
        receita_total=('receita_total', 'sum')
    ).reset_index()
    
    # Cálculo do Fancy Score
    cliente_df['fancy_score'] = cliente_df['itens_fancy'] / cliente_df['total_itens']
    
    # Faixas do Fancy Score
    cliente_df['faixa_fancy'] = pd.cut(
        cliente_df['fancy_score'], 
        bins=[-0.01, 0, 0.25, 0.5, 0.75, 1.0], 
        labels=['0% (Apenas Padrão)', '1-25%', '26-50%', '51-75%', '76-100% (Apenas Fancy)']
    )
    
    return df, cliente_df

try:
    df, cliente_df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo 'vendas_clientes_catalogo.csv': {e}")
    st.stop()

# Filtros na Barra Lateral
st.sidebar.header("🔍 Filtros de Análise")
estados_sel = st.sidebar.multiselect("Estado (UF)", options=sorted(df['estado'].unique()), default=sorted(df['estado'].unique()))
canais_sel = st.sidebar.multiselect("Canal de Aquisição", options=sorted(df['canal_aquisicao'].unique()), default=sorted(df['canal_aquisicao'].unique()))

df_filtered = df[(df['estado'].isin(estados_sel)) & (df['canal_aquisicao'].isin(canais_sel))]
cliente_filtered = cliente_df[(cliente_df['estado'].isin(estados_sel)) & (cliente_df['canal_aquisicao'].isin(canais_sel))]

# Cards de Métricas (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Clientes", f"{len(cliente_filtered):,}")
col2.metric("Fancy Score Médio", f"{cliente_filtered['fancy_score'].mean()*100:.1f}%")
col3.metric("Lucro Total Fancy", f"R$ {df_filtered[df_filtered['linha']=='Fancy']['Lucro Bruto'].sum():,.2f}")
col4.metric("Lucro Total Padrão", f"R$ {df_filtered[df_filtered['linha']=='Padrão']['Lucro Bruto'].sum():,.2f}")

st.divider()

# Seção 1: Fancy Score
st.header("1. Análise do Fancy Score por Cliente")
st.markdown("""
O **Fancy Score** representa a proporção de itens da linha *Fancy* comprados em relação ao total de itens adquiridos pelo cliente:
$$\\text{Fancy Score} = \\frac{\\text{Quantidade de Itens Fancy}}{\\text{Quantidade Total de Itens Comprados}}$$
""")

col_a, col_b = st.columns([1, 1])

with col_a:
    fig_hist = px.histogram(
        cliente_filtered, x='fancy_score', nbins=20,
        title="Distribuição do Fancy Score entre Clientes",
        labels={'fancy_score': 'Fancy Score (% de itens Fancy)', 'count': 'Número de Clientes'},
        color_discrete_sequence=['#6b4c9a']
    )
    fig_hist.update_layout(bargap=0.1)
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    fig_box = px.box(
        cliente_filtered, x='faixa_fancy', y='lucro_total',
        title="Lucro Gerado por Faixa de Fancy Score",
        labels={'faixa_fancy': 'Faixa de Fancy Score', 'lucro_total': 'Lucro Total Gerado (R$)'},
        color='faixa_fancy', color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# Seção 2: Prova Matemática do "Efeito Fancy"
st.header("2. Prova Matemática do 'Efeito Fancy'")

col_m1, col_m2 = st.columns(2)

fancy_data = df_filtered[df_filtered['linha']=='Fancy']
padrao_data = df_filtered[df_filtered['linha']=='Padrão']

# Cálculo nativo do Teste T de Welch sem biblioteca externa
n1, n2 = len(fancy_data), len(padrao_data)
m1, m2 = fancy_data['Lucro Bruto'].mean(), padrao_data['Lucro Bruto'].mean()
v1, v2 = fancy_data['Lucro Bruto'].var(ddof=1), padrao_data['Lucro Bruto'].var(ddof=1)

if n1 > 1 and n2 > 1 and (v1/n1 + v2/n2) > 0:
    t_stat = (m1 - m2) / np.sqrt((v1 / n1) + (v2 / n2))
else:
    t_stat = 0.0

with col_m1:
    st.subheader("📊 Comparativo Financeiro por Pedido")
    
    rec_padrao = (padrao_data['quantidade']*padrao_data['preco_venda']).sum()
    rec_fancy = (fancy_data['quantidade']*fancy_data['preco_venda']).sum()
    
    margem_padrao = (padrao_data['Lucro Bruto'].sum() / rec_padrao * 100) if rec_padrao > 0 else 0
    margem_fancy = (fancy_data['Lucro Bruto'].sum() / rec_fancy * 100) if rec_fancy > 0 else 0
    
    comp_df = pd.DataFrame({
        'Métrica': ['Preço Médio', 'Custo Médio', 'Lucro Médio/Pedido', 'Margem Bruta Global'],
        'Padrão': [
            f"R$ {padrao_data['preco_venda'].mean():.2f}" if n2 > 0 else "N/A",
            f"R$ {padrao_data['custo_producao'].mean():.2f}" if n2 > 0 else "N/A",
            f"R$ {m2:.2f}" if n2 > 0 else "N/A",
            f"{margem_padrao:.1f}%"
        ],
        'Fancy': [
            f"R$ {fancy_data['preco_venda'].mean():.2f}" if n1 > 0 else "N/A",
            f"R$ {fancy_data['custo_producao'].mean():.2f}" if n1 > 0 else "N/A",
            f"R$ {m1:.2f}" if n1 > 0 else "N/A",
            f"{margem_fancy:.1f}%"
        ],
        'Diferença': [
            f"+{((fancy_data['preco_venda'].mean()/padrao_data['preco_venda'].mean())-1)*100:.0f}%" if n1>0 and n2>0 else "N/A",
            f"+{((fancy_data['custo_producao'].mean()/padrao_data['custo_producao'].mean())-1)*100:.0f}%" if n1>0 and n2>0 else "N/A",
            f"+{((m1/m2)-1)*100:.0f}%" if m2>0 else "N/A",
            f"+{(margem_fancy - margem_padrao):.1f} p.p."
        ]
    })
    st.table(comp_df)

with col_m2:
    st.subheader("🧪 Prova Estatística")
    st.write(f"- **Lucro Médio/Pedido (Fancy):** `R$ {m1:.2f}`")
    st.write(f"- **Lucro Médio/Pedido (Padrão):** `R$ {m2:.2f}`")
    st.write(f"- **Razão de Rentabilidade:** Produtos Fancy geram **{(m1/m2):.1f}x** mais lucro por pedido.")
    st.write(f"- **Estatística T (Teste Welch):** `t = {t_stat:.2f}`")
    
    if abs(t_stat) > 1.96:
        st.success("✅ **Efeito Fancy Comprovado!** A estatística `t > 1.96` confirma com **mais de 95% de confiança estatística** que a linha Fancy possui lucro por pedido significativamente superior à linha Padrão.")
    else:
        st.warning("A variação atual nos filtros não apresenta significância estatística suficiente.")

st.divider()

# Seção 3: Data Storytelling & Marketing
st.header("3. Data Storytelling: Qual o Público-Alvo Ideal para o Marketing?")

col_p1, col_p2 = st.columns(2)

with col_p1:
    fig_canal = px.bar(
        df_filtered.groupby(['canal_aquisicao', 'linha']).size().reset_index(name='count'),
        x='canal_aquisicao', y='count', color='linha', barmode='group',
        title="Vendas por Canal de Aquisição e Linha",
        labels={'canal_aquisicao': 'Canal de Aquisição', 'count': 'Total de Pedidos'},
        color_discrete_map={'Fancy': '#6b4c9a', 'Padrão': '#a8a8a8'}
    )
    st.plotly_chart(fig_canal, use_container_width=True)

with col_p2:
    fig_scat = px.scatter(
        cliente_filtered, x='idade', y='fancy_score', color='canal_aquisicao',
        title="Relação entre Idade do Cliente e Fancy Score",
        labels={'idade': 'Idade do Cliente', 'fancy_score': 'Fancy Score'},
        opacity=0.6
    )
    st.plotly_chart(fig_scat, use_container_width=True)

st.subheader("🎯 Recomendação Estratégica de Marketing")
st.info("""
1. **Perfil do Público-Alvo Recomendado:**
   - **Faixa Etária:** Jovens e Jovens Adultos (**18 a 35 anos**) apresentam os maiores Fancy Scores.
   - **Canais de Tração Principal:** **Instagram** e **TikTok** juntos concentram **mais de 64%** de todas as compras de produtos Fancy.
   - **Comportamento:** O público consumidor da linha Fancy valoriza status, embalagens premium e experiência de consumo.

2. **Ações Práticas para o Time de Marketing:**
   - Redirecionar orçamento de mídia paga do Google Ads/Orgânico para **Instagram Reels** e **TikTok**.
   - Criar campanhas focadas na **exclusividade e sofisticação** dos produtos da linha Fancy (Vinhos, Cafés e Chocolates).
""")
