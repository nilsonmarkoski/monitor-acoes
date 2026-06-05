import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

# ---------------- Configuração da página ----------------
st.set_page_config(
    page_title="📈 Ichimoku Cloud Viewer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Visualização do Ichimoku Cloud")
st.markdown(
    "Escolha uma ação para visualizar o **Ichimoku Kinko Hyo** com recursos gráficos interativos.")

# ---------------- Seleção do ticker ----------------
acao = st.selectbox(
    'Escolha o ticker da ação:',
    (
        "LOGG3.SA", "LIGT3.SA", "USIM3.SA", "PLPL3.SA", "BBSE3.SA", "ITUB4.SA",
        "WEGE3.SA", "BTAL11.SA", "BBAS3.SA", "RDCD3.SA", "PSSA3.SA", "ENGI3.SA",
        "CPLE3.SA", "KEPL3.SA", "PETR4.SA", "CMIG4.SA", "MGLU3.SA"
    ),
    key="ticker"
)

# ---------------- Download dos dados ----------------
df = yf.download(acao, period="5y")
df.dropna(inplace=True)

# ---------------- Parâmetros Ichimoku ----------------
tenkan_period = 9
kijun_period = 26
senkou_span_b_period = 52
chikou_shift = 26

# ---------------- Cálculo Ichimoku ----------------
df['Tenkan_sen'] = (df['High'].rolling(tenkan_period).max() +
                    df['Low'].rolling(tenkan_period).min()) / 2
df['Kijun_sen'] = (df['High'].rolling(kijun_period).max() +
                   df['Low'].rolling(kijun_period).min()) / 2
df['Senkou_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(chikou_shift)
df['Senkou_B'] = ((df['High'].rolling(senkou_span_b_period).max(
) + df['Low'].rolling(senkou_span_b_period).min()) / 2).shift(chikou_shift)
df['Chikou_span'] = df['Close'].shift(-chikou_shift)

df.dropna(inplace=True)

# ---------------- Gráfico interativo Plotly ----------------
fig = go.Figure()

# Preço de fechamento (candlestick)
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name="Preço",
    increasing_line_color="green",
    decreasing_line_color="red",
    showlegend=True
))

# Linhas Ichimoku
fig.add_trace(go.Scatter(x=df.index, y=df['Tenkan_sen'], line=dict(
    color="blue", width=1.5), name="Tenkan-sen (Conversão)"))
fig.add_trace(go.Scatter(x=df.index, y=df['Kijun_sen'], line=dict(
    color="red", width=1.5), name="Kijun-sen (Base)"))
fig.add_trace(go.Scatter(x=df.index, y=df['Chikou_span'], line=dict(
    color="purple", width=1.5, dash="dot"), name="Chikou Span"))

# Senkou A e B
fig.add_trace(go.Scatter(x=df.index, y=df['Senkou_A'], line=dict(
    color="green", width=1.5), name="Senkou Span A"))
fig.add_trace(go.Scatter(x=df.index, y=df['Senkou_B'], line=dict(
    color="orange", width=1.5), name="Senkou Span B"))

# Nuvem verde (Senkou A > Senkou B)
fig.add_trace(go.Scatter(
    x=df.index.tolist() + df.index[::-1].tolist(),
    y=df['Senkou_A'].tolist() + df['Senkou_B'][::-1].tolist(),
    fill="toself",
    fillcolor="rgba(0, 255, 0, 0.2)",
    line=dict(color="rgba(0,0,0,0)"),
    name="Kumo (Bullish)",
    showlegend=True
))

# Nuvem vermelha (Senkou B > Senkou A)
fig.add_trace(go.Scatter(
    x=df.index.tolist() + df.index[::-1].tolist(),
    y=df['Senkou_B'].tolist() + df['Senkou_A'][::-1].tolist(),
    fill="toself",
    fillcolor="rgba(255, 0, 0, 0.2)",
    line=dict(color="rgba(0,0,0,0)"),
    name="Kumo (Bearish)",
    showlegend=True
))

# Layout
fig.update_layout(
    title=f"Ichimoku Cloud - {acao}",
    yaxis_title="Preço (R$)",
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom",
                y=1.02, xanchor="right", x=1),
    height=700
)

# ---------------- Exibir no Streamlit ----------------
st.plotly_chart(fig, use_container_width=True)

# Mostrar últimos valores
st.subheader("📋 Últimos dados calculados")
st.dataframe(df.tail(10))
