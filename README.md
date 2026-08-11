# 🍷 GourmetBox DataLab: Investigação do "Efeito Fancy"

> **Estudo de caso end-to-end de inteligência de negócios e análise estatística de dados de e-commerce.**

---

## 📌 Descrição do Projeto

O **GourmetBox DataLab** realizou uma investigação aprofundada para comprovar e quantificar o **"Efeito Fancy"** no comportamento de compra dos clientes. O projeto unificou e tratou bases relacionais dispersas em ecossistemas de **CRM, ERP e E-commerce** utilizando **Python e Pandas**.

Além do tratamento de dados, o projeto contou com **Feature Engineering** para criar métricas estratégicas (como *Margem Bruta*, *Ticket Médio* e o autoral *Fancy Score*), além de testes de hipótese estatísticos e um **Dashboard Interativo** desenvolvido em Streamlit.

---

## 🚀 Acesse a Aplicação

🔗 **[Clique aqui para navegar no Dashboard Interativo do Efeito Fancy](https://estudodecasoefeitofancy-bvp5hwwjpqhsggydah9ynm.streamlit.app/)**

---

## 📊 Estrutura de Métricas Criadas (Feature Engineering)

* **Fancy Score:** Proporção individual de itens adquiridos da linha *Fancy* sobre o volume total do pedido de cada cliente.
* **Margem Bruta (%):** Cálculo da rentabilidade real por categoria, isolando os custos de produção e frete do preço final de venda.
* **Ticket Médio & Valor de Vida (LTV):** Segmentação do comportamento financeiro do cliente por canal de aquisição e faixa etária.

---

## 🔬 Resultados da Investigação ("Efeito Fancy")

A análise estatística e o cruzamento dos dados unificados provaram matematicamente a existência do fenômeno:

* **💡 Inversão por Faixa de Renda:** Clientes pertencentes à faixa de **Baixa Renda** concentram o maior *Fancy Score* médio (**37,3%**), enquanto a faixa de **Alta Renda** registra apenas **16,4%**.
* **🎂 Faixa Etária Proeminente:** Jovens entre **18 e 35 anos** possuem um *Fancy Score* superior a **50%**, consolidando-se como os principais impulsionadores e consumidores da linha premium.
* **📱 Canais de Aquisição:** Clientes captados via **TikTok (52,3%)** e **Instagram (45,2%)** apresentam a maior taxa de adesão e conversão de itens *Fancy*.
* **📈 Prova Estatística:** Testes de hipótese (Welch's t-test) confirmaram com mais de **95% de confiança estatística** ($t > 1.96$) que a rentabilidade por pedido da linha *Fancy* é significativamente superior à linha *Padrão*.

---

## 🎯 Recomendações Estratégicas para o Marketing

1. **Público-Alvo Prioritário:** Focar esforços de engajamento e aquisição nos jovens de **18 a 35 anos**.
2. **Canais de Foco:** Concentrar os investimentos de mídia paga e branding no **TikTok** e **Instagram** (mídias visuais e baseadas em experiência).
3. **Posicionamento de Marca:** Trabalhar a comunicação da linha *Fancy* sob a narrativa de **"pequeno luxo cotidiano acessível"** ou **"recompensa diária"**, conectando-se diretamente com o comportamento do público jovem.

---

## 🛠️ Tecnologias & Ferramentas Utilizadas

* **Linguagem & Manipulação de Dados:** Python, Pandas e NumPy (Análise exploratória, tratamento e merge das bases no Google Colab)
* **Visualização & Dashboard:** Plotly Express e Streamlit
* **Deploy & Hospedagem:** GitHub e Streamlit Community Cloud
* **Apoio ao Desenvolvimento:** IA Generativa (Gemini e ChatGPT) para auxílio no raciocínio estatístico, modelagem de dados e estruturação do dashboard.

---

### 📂 Como executar o projeto localmente

```bash
# Clone o repositório
git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)

# Entre no diretório do projeto
cd SEU-REPOSITORIO

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação Streamlit
streamlit run Dashboard_app.py
