import pandas as pd 
import matplotlib.pyplot as plt
import yfinance as yf 
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Meu Aplicativo Incrível",layout='wide', initial_sidebar_state='expanded')

#------------------------------------------------------------------
st.write("Ação que você irá escolher!")
#--ESCLOLHA DA AÇÃO
acao = st.selectbox('Escolha o ticker da ação!',("LOGG3.SA","LIGT3.SA","USIM3.SA","PLPL3.SA","BBSE3.SA","ITUB4.SA",
                    "WEGE3.SA","BTAL11.SA","BBAS3.SA","RDCD3.SA","PSSA3.SA","PLPL3.SA","ENGI3.SA",
                    "CPLE3.SA","KEPL3.SA","PETR4.SA","CMIG4.SA","MGLU3.SA"),key=1 )
#pegar a ação que queremos trabalhar 
st.write(acao)
carteira = yf.download(acao, period="5y")
carteira.dropna(inplace=True)
#IMPORTANTE TRANSFORMO EM UM DATAFRAME 
df = pd.DataFrame(carteira)
st.table(df.tail())
#define o comprimento de tenkan Sen  ou conversão da linha 
cl_period  = 10 
#define o comprimento de Kijun Sen ou linha base 
bl_period = 30
#define o comprimento de Senkou Sen B ou intervalo do lado principal
lead_span_b_period = 60
#define o comprimento de intervalo Chikou ou intervalo principal
lag_span_period = 5
#calcula a conversão da linha 
high_20 =df['High'].rolling(cl_period).max()
low_20 = df['Low'].rolling(cl_period).min()
df["Conversao_linha"]= (high_20+low_20)/2

#calcular a linha base 
high_60 =df['High'].rolling(bl_period).max()
low_60 = df['Low'].rolling(bl_period).min()
df['Linha_base'] = (high_60+low_60)/2

#calcula  intervalo principal de A
df["Intervalo_principal_A"]=((df.Conversao_linha + df.Linha_base)/2).shift(lag_span_period)

#calcular intervao principal B
high_120 = df['High'].rolling(120).max()
low_120 = df['Low'].rolling(120).min()
df["Intervalo_principal_B"]=((high_120 + low_120)/2).shift(lead_span_b_period)
#calcula o lagging span 
df["lagging_span"]= df["Close"].shift(-lag_span_period)
#apaga os campos vazios con NA
df.dropna(inplace=True)
st.table(df.tail())
#adiciona figura e objeto axis 

fig = go.Figure()


fig , ax = plt.subplots(1,1, sharex=True, figsize=(20,9))

#plot Close com index na x-axis uma linha de 4
ax.plot(df.index,df['Close'],linewidth=4)

ax.plot(df.index, df['Intervalo_principal_A'])
ax.plot(df.index, df['Intervalo_principal_B'])

ax.fill_between(df.index, df['Intervalo_principal_A'], df["Intervalo_principal_B"],
                    where=df['Intervalo_principal_A']>=df["Intervalo_principal_B"], 
                    color= "lightgreen")

ax.fill_between(df.index, df['Intervalo_principal_B'],df["Intervalo_principal_A"],
                    where=df['Intervalo_principal_A']<df["Intervalo_principal_B"], 
                    color= "lightcoral")

plt.legend(loc=0)
plt.grid()

st.pyplot(fig)





