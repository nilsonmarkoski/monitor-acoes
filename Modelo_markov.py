import numpy as np
import streamlit as st
import pandas as pd
import yfinance as yf
from hmmlearn import hmm
import matplotlib.pyplot as plt
import os

os.environ['OMP_NUM_THREADS'] = '1'
st.set_page_config(page_title="Meu Aplicativo Incrível",
                   layout='wide', initial_sidebar_state='expanded')


""""Use modelos de Markov para detectar mudanças de regime
Um Modelo Oculto de Markov (HMM) é um modelo probabilístico onde uma sequência de variáveis ​​observáveis ​​é gerada 
por uma sequência de estados ocultos. O importante a notar é que os estados ocultos não são observados diretamente.
As variáveis ​​observadas podem ser coisas como preço, enquanto os estados ocultos podem ser um regime de mercado.
As transições entre estados ocultos assumem a forma de uma cadeia de Markov. Eles podem ser especificados pela 
probabilidade inicial e por uma matriz de transição.
A probabilidade de emissão de uma variável observável pode ser qualquer distribuição baseada 
no estado oculto."""


acao = "PSSA3.SA"
carteira = yf.download(acao, period="10y", multi_level_index=False)
carteira.dropna(inplace=True)
retorna = np.log(carteira['Close']/carteira['Close'].shift(1))
range = (carteira["High"]-carteira["Low"])
caracteristicas = pd.concat([retorna, range], axis=1).dropna()
caracteristicas.columns = ["retorna", "range"]
st.table(carteira.tail())
st.table(caracteristicas.tail())
"""Inicializamos um HMM com emissões gaussianas. Esta é uma suposição simplificada de que as observações 
no HMM seguem uma distribuição normal.
Configuramos o modelo para ter três estados ocultos, representando diferentes regimes de mercado, como mercados
 em alta, mercados planos e mercados em baixa.
Definimos o tipo de covariância como “full”, indicando que as matrizes de covariância das distribuições 
gaussianas associadas a cada estado estão totalmente parametrizadas. Isto significa que a distribuição de 
cada estado tem a sua própria matriz de covariância completa que permite correlações entre diferentes dimensões dos dados.
Em seguida, treinamos o modelo nos recursos. Durante o treinamento, ajustamos iterativamente os ]
parâmetros do modelo ao longo de 1.000 iterações para maximizar a probabilidade dos recursos observados, dados os estados ocultos
Este último passo é a magia que aprende os padrões subjacentes e as transições entre os regimes de mercado.
Assim que o modelo estiver ajustado, podemos usar o modelo treinado para prever os estados ocultos dos recursos de entrada."""
model = hmm.GaussianHMM(
    n_components=3,
    covariance_type="full",
    n_iter=1000,
)
model.fit(caracteristicas)
"""Os estados previstos são retornados como um array NumPy que usamos para criar uma série de pandas. 
O resultado é um histograma que mostra o número de estados diários nos dados."""
estado = pd.Series(model.predict(caracteristicas), index=carteira.index[1:])
estado.name = "state"
estado.hist()
st.pyplot(plt.gcf())
"""Use modelos de Markov para detectar mudanças de regime. Há rumores de que a Renaissance Technologies usa 
    modelos ocultos de Markov em suas negociações.
Visualize os regimes
Finalmente, podemos representar graficamente os dados de preços coloridos por cada um dos vários estados."""
color_map = {
    0.0: "green",
    1.0: "orange",
    2.0: "red"
}

pd.concat([carteira["Close"], estado], axis=1).dropna().set_index("state", append=True)[
    "Close"].unstack("state").plot(color=color_map, figsize=[16, 12])

st.pyplot(plt.gcf())

"""Use modelos de Markov para detectar mudanças de regime. Há rumores de que a Renaissance Technologies usa modelos 
ocultos de Markov em suas negociações.
O modelo faz um bom trabalho detectando várias condições de mercado, incluindo tendências ascendentes 
(verde), movimentos descendentes (vermelho) e mercados laterais (laranja).
É importante notar que a suposição do modelo de uma distribuição gaussiana pode não capturar com
 precisão as complexidades dos dados do mercado financeiro. Como sabemos, os mercados apresentam
   tipicamente um comportamento anormal.
Observe também que sua saída será diferente, pois um HMM é um modelo probabilístico."""
