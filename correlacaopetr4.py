import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Petróleo vs PETR4", layout="wide")
st.title("📈 Correlação: Preço do Petróleo Brent vs Ação PETR4")

# Sidebar para inputs do usuário
with st.sidebar:
    st.header("Parâmetros")
    start_date = st.date_input(
        "Data Inicial",
        value=datetime(2019, 1, 1),
        min_value=datetime(2010, 1, 1))
    end_date = st.date_input(
        "Data Final",
        value=datetime(2025, 10, 27))
    update_button = st.button("Atualizar Dados")

# Baixar dados do Yahoo Finance


@st.cache_data
def load_data(start, end):
    try:
        # Baixar dados - retorna DataFrames completos
        brent_df = yf.download('BZ=F', start=start,
                               end=end, multi_level_index=False)
        petr4_df = yf.download('PETR4.SA', start=start,
                               end=end, multi_level_index=False)

        # Criar DataFrame combinado
        df = pd.DataFrame({
            'Brent_USD': brent_df['Close'],
            'PETR4_BRL': petr4_df['Close']
        }).dropna()

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()


if update_button or 'df' not in st.session_state:
    df = load_data(start_date, end_date)
    st.session_state.df = df
else:
    df = st.session_state.df

# Verificar se temos dados
if df.empty:
    st.warning("Nenhum dado disponível para o período selecionado.")
    st.stop()

# Calcular correlação
correlacao = np.corrcoef(df['Brent_USD'], df['PETR4_BRL'])[0, 1]

# Layout principal
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader(
        f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
with col2:
    st.metric("Correlação", f"{correlacao:.2f}")

# Gráfico
fig, ax1 = plt.subplots(figsize=(12, 6))

# Brent (USD)
ax1.plot(df.index, df['Brent_USD'], color='#1f77b4', label='Brent (USD)')
ax1.set_xlabel("Data")
ax1.set_ylabel("Preço do Brent (USD)", color='#1f77b4')
ax1.tick_params(axis='y', labelcolor='#1f77b4')
ax1.grid(True, linestyle='--', alpha=0.3)

# PETR4 (BRL)
ax2 = ax1.twinx()
ax2.plot(df.index, df['PETR4_BRL'], color='#2ca02c', label='PETR4 (BRL)')
ax2.set_ylabel("Preço PETR4 (BRL)", color='#2ca02c')
ax2.tick_params(axis='y', labelcolor='#2ca02c')

# Formatação
plt.title("Relação Histórica: Preço do Petróleo vs Ação da Petrobras")
fig.legend(loc="upper left", bbox_to_anchor=(0.15, 0.85))

# Melhorar formatação de datas
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b/%Y'))
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig)

# Tabela com dados
st.subheader("Dados Históricos")
st.dataframe(df.sort_index(ascending=False).head(10))

# Explicação
with st.expander("📌 Como interpretar?"):
    st.write("""
    - **Correlação próxima de 1**: PETR4 e petróleo tendem a subir/descer juntos
    - **Correlação próxima de -1**: Movimentos opostos
    - **Correlação próxima de 0**: Pouca relação direta
    """)
    st.write(
        f"**Neste período:** {'Forte correlação' if abs(correlacao) > 0.7 else 'Correlação moderada' if abs(correlacao) > 0.3 else 'Fraca correlação'} ({correlacao:.2f})")

# Rodapé
st.caption("Dados do Yahoo Finance | Atualizado em " +
           datetime.now().strftime("%d/%m/%Y"))
