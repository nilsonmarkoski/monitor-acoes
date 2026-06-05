# importar as bibliotecas
import yfinance as yf
import pandas as pd
import numpy as np
import chart_studio.plotly as pio
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Meu Aplicativo Incrível",
                   layout='wide', initial_sidebar_state='expanded')

# ------------------------------------------------------------------
st.write("Ação que você irá escolher!")
# --ESCLOLHA DA AÇÃO
acao = st.selectbox('Escolha o ticker da ação!', ("VULC3.SA", "POMO3.SA", 'KEPL3.SA', 'LOGG3.SA', 'ABCB4.SA', 'ALUP11.SA', 'B3SA3.SA', 'BRSR6.SA', 'BBSE3.SA', 'BRAP4.SA', 'BBAS3.SA', 'AGRO3.SA', 'CMIG3.SA', 'CMIG4.SA',
                                                  'CSMG3.SA', 'CPLE6.SA', 'CPFE3.SA', 'CMIN3.SA', 'CURY3.SA', 'DIRR3.SA', 'EGIE3.SA', 'FESA4.SA', 'GGBR4.SA', 'GOAU4.SA', 'MYPK3.SA', 'RANI3.SA', 'ITSA4.SA', 'JBSS3.SA',
                                                  'JHSF3.SA', 'LAVV3.SA', 'MRFG3.SA', 'BEEF3.SA', 'PETR3.SA', 'PETR4.SA', 'PSSA3.SA', 'RAPT4.SA', 'ROMI3.SA',
                                                  'SANB11.SA', 'CSNA3.SA', 'TAEE11.SA', 'VIVT3.SA', 'TRPL4.SA', 'TRIS3.SA', 'UNIP6.SA', 'USIM5.SA', 'VALE3.SA', 'VBBR3.SA', "MGLU3.SA"), key=1)

# -----selectbox---------------------------------------------------------------------------------------------------------------------------
codigo = st.selectbox('Escolha o prazo a ser escolhido!', ("1 dia", "5 dias",
                      "7 dias", "1 mês", "3 meses", "6 meses", "1 ano", "3 anos", "5 anos"))

match codigo:
    case "1 dia":
        codigo = "1d"
    case "5 dias":
        codigo = "5d"
    case "7 dias":
        codigo = "7d"
    case "1 mês":
        codigo = "1mo"
    case "3 meses":
        codigo = "3mo"
    case "6 meses":
        codigo = "6mo"
    case "1 ano":
        codigo = "1y"
    case "1 ano":
        codigo = "3y"
    case "1 ano":
        codigo = "5y"
    case _:
        codigo = "10y"

# ------------------------------------------------------------------
dias = st.number_input("Coloque o a médias de dias para a banda.")
st.write(dias)
# pegar a ação que queremos trabalhar
# acao = "PSSA3.SA"
# periodo = "1y" #"1d"  "1mo"   interval ="1m" "5m"
st.write(acao)

# codigo - periodo vou mdar isso mais tarde
carteira = yf.download(acao, period=codigo, multi_level_index=False)
# carteira.xs(acao, axis=1, level="Ticker")

# carteira = yf.Ticker(acao, start="2024-01-01")
# carteira = carteira.history(period=codigo)
# carteira.dropna(inplace=True)
# st.write(carteira)
# IMPORTANTE TRANSF
# ORMO EM UM DATAFRAME
df = pd.DataFrame(carteira)
# df.xs(acao, axis=1, level="Ticker")


# st.table(df.tail(10))

# calcular a média móvel 20 30 QUANTO QUIZER periodos
mm = df.rolling(window=int(dias)).mean()
mm.dropna(inplace=True)
st.write(mm.tail())

# calculo do descvio padrão
dpm = df.rolling(window=int(dias)).std()
dpm.dropna(inplace=True)
# print(dpm)

# cálculo da banda média superior e inferior -media movel = 2 vezes desvio padrao (acima e baixo)
sup_band = mm + 2 * dpm
inf_band = mm - 2 * dpm
# print(inf_band)

# cria e altera o nome das colunas de banda superior e inferior
sup_band = sup_band.rename(columns={'Close': 'superior'})
inf_band = inf_band.rename(columns={'Close': "inferior"})


# unir colunas de banda bollinger
# bandas_bollinger = df.join(sup_band).join(inf_band)
bandas_bollinger = df.join(sup_band['superior']).join(inf_band['inferior'])
bandas_bollinger.dropna(inplace=True)


# cálculo dos pontos de compra e venda
compra = bandas_bollinger[bandas_bollinger['Close']
                          <= bandas_bollinger["inferior"]]
venda = bandas_bollinger[bandas_bollinger['Close']
                         >= bandas_bollinger["superior"]]

# pio.templates.default = "plotly_dark"


fig = go.Figure()

fig.add_trace(go.Scatter(
    x=inf_band.index,
    y=inf_band["inferior"],
    name="Banda Inferior",
    line_color="rgba(173,204,255,0.2)"
))
fig.add_trace(go.Scatter(
    x=sup_band.index,
    y=sup_band["superior"],
    name="Banda superior",
    fill='tonexty',
    fillcolor="rgba(173,204,255,0.2)",
    line_color="rgba(173,204,255,0.2)"
))
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['Close'],
    name="Preço de fechamento",
    line_color=("#636EFA")
))
fig.add_trace(go.Scatter(
    x=mm.index,
    y=mm['Close'],
    name="Média Móvel",
    line_color=("#FECB52")
))
fig.add_trace(go.Scatter(
    x=compra.index,
    y=compra['Close'],
    name="Compra",
    mode="markers",
    marker=dict(color="#00CC96", size=8)
))
fig.add_trace(go.Scatter(
    x=venda.index,
    y=venda['Close'],
    name="Venda",
    mode="markers",
    marker=dict(color="#EF553B", size=8)
))

fig.update_layout(title_text=acao)

fig
