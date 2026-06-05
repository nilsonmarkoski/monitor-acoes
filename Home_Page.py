import streamlit as st

st.set_page_config(
    page_title="Monitor B3",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Monitor de Ações — B3")
st.markdown("---")

st.markdown("""
### Bem-vindo ao painel de acompanhamento da Bolsa brasileira b3

Use o menu lateral para navegar entre as páginas:

| Página | Descrição |
|--------|-----------|
| 📊 Dashboard B3 | Compare o desempenho relativo entre ações |
| 🔔 Monitor de Alertas | Acompanhe preços com alertas via WhatsApp |
| 📉 Comparativo | Análise técnica com SMA e RSI |
| 🗃️ Dados Brutos | Tabela completa de cotações |
""")

st.info("Selecione uma página no menu à esquerda para começar.", icon="👈")



