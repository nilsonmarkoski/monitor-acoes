import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go

# ---------------- Configuração da página ----------------
st.set_page_config(page_title="Bollinger + RSI Backtest", layout="wide")
st.title("📊 Bandas de Bollinger + RSI com Backtest")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Parâmetros")

    # Lista de ações populares do Brasil
    tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA",
               "MGLU3.SA", "BBDC4.SA", "ABEV3.SA"]

    # Seleção de ticker ou entrada manual
    ticker = st.selectbox("Selecione o ativo:", tickers, index=0)
    custom_ticker = st.text_input(
        "Ou digite outro ticker (ex: AAPL, MSFT):", "")
    if custom_ticker.strip() != "":
        ticker = custom_ticker.strip().upper()

    # Seleção de datas
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data inicial", datetime(2023, 1, 1))
    with col2:
        end_date = st.date_input("Data final", datetime.today())

    # Parâmetros de Bollinger e RSI
    window = st.slider("Janela da média móvel (dias)", 5, 50, 20)
    num_std = st.slider("Número de desvios padrão", 1.0, 3.0, 2.0, step=0.1)
    rsi_period = st.slider("Período RSI", 5, 30, 14)

# ---------------- Função para carregar dados ----------------


@st.cache_data
def load_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end)
        df.reset_index(inplace=True)
        # Corrigir multi-index ou colunas duplicadas
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()]
        return df
    except:
        st.error("Erro ao carregar dados. Verifique o código do ativo.")
        return None


df = load_data(ticker, start_date, end_date)

if df is not None and not df.empty:
    # ---------------- Bandas de Bollinger ----------------
    df['MA'] = df['Close'].rolling(window=window).mean()
    df['STD'] = df['Close'].rolling(window=window).std()
    df['Upper'] = df['MA'] + df['STD'] * num_std
    df['Lower'] = df['MA'] - df['STD'] * num_std
    df['Pos_Relativa'] = (df['Close'] - df['Lower']) / \
        (df['Upper'] - df['Lower'])

    # ---------------- RSI ----------------
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=rsi_period, min_periods=1).mean()
    avg_loss = loss.rolling(window=rsi_period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # ---------------- Sinais de Compra/Venda ----------------
    df['Buy_Signal'] = (df['Close'] <= df['Lower']) & (df['RSI'] < 30)
    df['Sell_Signal'] = (df['Close'] >= df['Upper']) & (df['RSI'] > 70)

    # ---------------- Backtest Simulado ----------------
    df['Position'] = 0
    position = 0
    for i in range(len(df)):
        if df['Buy_Signal'].iloc[i] and position == 0:
            position = 1
        elif df['Sell_Signal'].iloc[i] and position == 1:
            position = 0
        df.at[i, 'Position'] = position

    df['Daily_Return'] = df['Close'].pct_change().fillna(0)
    df['Strategy_Return'] = df['Daily_Return'] * df['Position']
    df['Strategy_Balance'] = (1 + df['Strategy_Return']).cumprod() * 10000
    df['Benchmark_Balance'] = (1 + df['Daily_Return']).cumprod() * 10000

    df['Peak'] = df['Strategy_Balance'].cummax()
    df['Drawdown'] = df['Strategy_Balance'] - df['Peak']
    max_dd = df['Drawdown'].min()

    # ---------------- Gráfico interativo Plotly ----------------
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines',
                  name='Preço Fechamento', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA'], mode='lines',
                  name=f'Média Móvel {window}d', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Upper'], mode='lines',
                  name='Banda Superior', line=dict(color='green', dash='dash')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Lower'], mode='lines',
                  name='Banda Inferior', line=dict(color='green', dash='dash')))
    fig.add_trace(go.Scatter(x=df['Date'][df['Buy_Signal']], y=df['Close'][df['Buy_Signal']],
                  mode='markers', name='Compra', marker=dict(symbol='triangle-up', size=12, color='green')))
    fig.add_trace(go.Scatter(x=df['Date'][df['Sell_Signal']], y=df['Close'][df['Sell_Signal']],
                  mode='markers', name='Venda', marker=dict(symbol='triangle-down', size=12, color='red')))
    fig.update_layout(title=f"Bandas de Bollinger + RSI - {ticker}",
                      xaxis_title="Data", yaxis_title="Preço (R$)", template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- Métricas ----------------
    st.subheader("📊 Métricas do Sistema")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Preço Atual", f"R$ {df['Close'].iloc[-1]:.2f}")
    col2.metric("Retorno Total (%)",
                f"{(df['Strategy_Balance'].iloc[-1]/10000 - 1)*100:.2f}%")
    col3.metric("Drawdown Máximo", f"R$ {max_dd:.2f}")
    col4.metric("Posição Atual",
                "Comprado" if df['Position'].iloc[-1] == 1 else "Sem posição")

    # ---------------- Gráfico de Saldo ----------------
    st.subheader("Saldo Simulado x Benchmark")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['Strategy_Balance'],
                   mode='lines', name='Estratégia', line=dict(color='purple')))
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['Benchmark_Balance'],
                   mode='lines', name='Benchmark', line=dict(color='orange')))
    fig2.update_layout(xaxis_title="Data",
                       yaxis_title="Saldo (R$)", template='plotly_white')
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- Últimos registros ----------------
    st.subheader("Últimos 5 registros")
    st.dataframe(df.tail())

else:
    st.warning("Nenhum dado disponível para os parâmetros selecionados.")
