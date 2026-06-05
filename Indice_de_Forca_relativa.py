import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
import streamlit as st

# ------------------ Configuração Streamlit ------------------
st.set_page_config(
    page_title="Análise RSI - Ações",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Função RSI ------------------


def calcular_RSI(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Calcula o Índice de Força Relativa (RSI) de um DataFrame de preços de fechamento."""

    df = df.copy()
    df['change'] = df['Close'].diff()

    df['gain'] = df['change'].clip(lower=0)
    df['loss'] = -df['change'].clip(upper=0)

    # Médias móveis exponenciais suavizadas (mais próximo da fórmula clássica)
    df['avg_gain'] = df['gain'].ewm(alpha=1/window, min_periods=window).mean()
    df['avg_loss'] = df['loss'].ewm(alpha=1/window, min_periods=window).mean()

    df['RS'] = df['avg_gain'] / df['avg_loss']
    df[f'RSI{window}'] = 100 - (100 / (1 + df['RS']))

    return df[['Close', f'RSI{window}']].copy()


# ------------------ Interface ------------------
st.title("📊 Análise Técnica - RSI")

# Seleção de ativo
acao = st.selectbox(
    "Escolha o ticker da ação:",
    (
        "VULC3.SA", "LOGG3.SA", "LIGT3.SA", "USIM3.SA", "PLPL3.SA", "BBSE3.SA",
        "ITUB4.SA", "WEGE3.SA", "BTAL11.SA", "BBAS3.SA", "RDCD3.SA", "PSSA3.SA",
        "ENGI3.SA", "CPLE3.SA", "KEPL3.SA", "PETR4.SA", "CMIG4.SA", "MGLU3.SA"
    )
)

# Download dos dados
data = yf.download(acao, period="1y")

# Se vier MultiIndex no DataFrame (yfinance às vezes traz isso), corrigir:
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

st.subheader(f"📈 Dados históricos - {acao}")
st.write(data.tail())

# Cálculo RSI
window = 20
df_rsi = calcular_RSI(data, window).dropna()
st.subheader(f"📊 Índice de Força Relativa ({window} dias)")
st.dataframe(df_rsi.tail(30))

# Garantir que RSI seja uma Series 1D
rsi = df_rsi[f'RSI{window}'].astype(float)

# Sinais de compra/venda
df_rsi['Buy_Signal'] = np.where(
    (rsi.shift(1) > 30) & (rsi < 30),
    df_rsi['Close'],
    np.nan
)

df_rsi['Sell_Signal'] = np.where(
    (rsi.shift(1) < 70) & (rsi > 70),
    df_rsi['Close'],
    np.nan
)

df_rsi = df_rsi.reset_index()

# ------------------ Gráfico ------------------
fig, ax = plt.subplots(figsize=(10, 5))

# Preço de fechamento
ax.plot(df_rsi['Date'], df_rsi['Close'],
        label="Preço Fechamento", color="blue")
ax.scatter(df_rsi['Date'], df_rsi['Buy_Signal'],
           label="Compra", marker="^", color="green", s=100)
ax.scatter(df_rsi['Date'], df_rsi['Sell_Signal'],
           label="Venda", marker="v", color="red", s=100)

# RSI
ax2 = ax.twinx()
ax2.plot(df_rsi['Date'], df_rsi[f'RSI{window}'],
         label=f"RSI {window}", color="gray", alpha=0.7)
ax2.axhline(70, color="red", ls="--", alpha=0.5)
ax2.axhline(30, color="green", ls="--", alpha=0.5)
ax2.set_ylabel(f"RSI {window}")

# Layout
ax.set_title(f"Estratégia RSI - {acao}", fontsize=14)
ax.set_xlabel("Data")
ax.set_ylabel("Preço (R$)")
ax.legend(loc="upper left")
ax2.legend(loc="upper right")
fig.autofmt_xdate()

st.pyplot(fig)
