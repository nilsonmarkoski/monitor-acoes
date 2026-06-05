import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Monitor de Ações B3",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

"""
# :material/query_stats: Monitor de Ações — B3

Compare ações da bolsa brasileira e acompanhe o desempenho relativo entre elas.
"""

""  # Espaço

cols = st.columns([1, 3])

# ─── Ações da B3 ───────────────────────────────────────────────────────────────
ACOES_B3 = [
    "ABEV3.SA", "ALPA4.SA", "AMER3.SA", "ASAI3.SA", "AZUL4.SA",
    "B3SA3.SA", "BBAS3.SA", "BBDC3.SA", "BBDC4.SA", "BBSE3.SA",
    "BEEF3.SA", "BPAC11.SA", "BRAP4.SA", "BRFS3.SA", "BRKM5.SA",
    "CASH3.SA", "CCRO3.SA", "CIEL3.SA", "CMIG4.SA", "CMIN3.SA",
    "COGN3.SA", "CPFE3.SA", "CPLE6.SA", "CRFB3.SA", "CSAN3.SA",
    "CSNA3.SA", "CVCB3.SA", "CYRE3.SA", "DXCO3.SA", "EGIE3.SA",
    "ELET3.SA", "ELET6.SA", "EMBR3.SA", "ENEV3.SA", "ENGI11.SA",
    "EQTL3.SA", "EZTC3.SA", "FLRY3.SA", "GGBR4.SA", "GOAU4.SA",
    "GOLL4.SA", "HAPV3.SA", "HYPE3.SA", "IGTI11.SA", "IRBR3.SA",
    "ITSA4.SA", "ITUB4.SA", "JBSS3.SA", "JHSF3.SA", "KLBN11.SA",
    "LREN3.SA", "LWSA3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA",
    "MULT3.SA", "NTCO3.SA", "PCAR3.SA", "PETR3.SA", "PETR4.SA",
    "PETZ3.SA", "PRIO3.SA", "QUAL3.SA", "RADL3.SA", "RAIL3.SA",
    "RDOR3.SA", "RENT3.SA", "RRRP3.SA", "SANB11.SA", "SBSP3.SA",
    "SLCE3.SA", "SMTO3.SA", "SOMA3.SA", "SUZB3.SA", "TAEE11.SA",
    "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "USIM5.SA", "VALE3.SA",
    "VBBR3.SA", "VIIA3.SA", "VIVT3.SA", "WEGE3.SA", "YDUQ3.SA",
]

ACOES_PADRAO = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "WEGE3.SA", "ABEV3.SA"]


def acoes_para_str(acoes):
    return ",".join(acoes)


if "tickers_input" not in st.session_state:
    st.session_state.tickers_input = st.query_params.get(
        "acoes", acoes_para_str(ACOES_PADRAO)
    ).split(",")


def atualizar_query_param():
    if st.session_state.tickers_input:
        st.query_params["acoes"] = acoes_para_str(st.session_state.tickers_input)
    else:
        st.query_params.pop("acoes", None)


celula_esq = cols[0].container(border=True, height="stretch", vertical_alignment="center")

with celula_esq:
    tickers = st.multiselect(
        "Selecione as ações",
        options=sorted(set(ACOES_B3) | set(st.session_state.tickers_input)),
        default=st.session_state.tickers_input,
        placeholder="Ex: PETR4.SA, VALE3.SA...",
        accept_new_options=True,
    )

# ─── Seletor de período ────────────────────────────────────────────────────────
horizonte_map = {
    "1 Mês":    "1mo",
    "3 Meses":  "3mo",
    "6 Meses":  "6mo",
    "1 Ano":    "1y",
    "5 Anos":   "5y",
    "10 Anos":  "10y",
    "20 Anos":  "20y",
}

with celula_esq:
    horizonte = st.pills(
        "Período",
        options=list(horizonte_map.keys()),
        default="6 Meses",
    )

tickers = [t.upper() for t in tickers]

# Garante sufixo .SA
tickers = [t if t.endswith(".SA") else t + ".SA" for t in tickers]

if tickers:
    st.query_params["acoes"] = acoes_para_str(tickers)
else:
    st.query_params.pop("acoes", None)

if not tickers:
    celula_esq.info("Selecione pelo menos uma ação para começar.", icon=":material/info:")
    st.stop()


celula_dir = cols[1].container(border=True, height="stretch", vertical_alignment="center")


@st.cache_resource(show_spinner="Carregando dados da B3...")
def carregar_dados(tickers, periodo):
    tickers_obj = yf.Tickers(" ".join(tickers))
    data = tickers_obj.history(period=periodo)
    if data is None:
        raise RuntimeError("Nenhum dado retornado pelo Yahoo Finance.")
    return data["Close"]


try:
    dados = carregar_dados(tuple(tickers), horizonte_map[horizonte])
except Exception as e:
    st.warning(f"Erro ao carregar dados: {e}")
    st.stop()

# Remove sufixo .SA dos nomes das colunas para exibição mais limpa
dados.columns = [c.replace(".SA", "") for c in dados.columns]
tickers_display = [t.replace(".SA", "") for t in tickers]

colunas_vazias = dados.columns[dados.isna().all()].tolist()
if colunas_vazias:
    st.error(f"Não foi possível carregar dados para: {', '.join(colunas_vazias)}")
    st.stop()

# Normaliza preços (base 1)
normalizado = dados.div(dados.iloc[0])

ultimos_valores = {normalizado[t].iat[-1]: t for t in tickers_display if t in normalizado.columns}
melhor = max(ultimos_valores.items())
pior   = min(ultimos_valores.items())

celula_inf_esq = cols[0].container(border=True, height="stretch", vertical_alignment="center")

with celula_inf_esq:
    colunas_metricas = st.columns(2)
    colunas_metricas[0].metric(
        "Melhor desempenho",
        melhor[1],
        delta=f"{round((melhor[0] - 1) * 100, 1)}%",
        width="content",
    )
    colunas_metricas[1].metric(
        "Pior desempenho",
        pior[1],
        delta=f"{round((pior[0] - 1) * 100, 1)}%",
        width="content",
    )

# Gráfico de preços normalizados
with celula_dir:
    st.altair_chart(
        alt.Chart(
            normalizado.reset_index().melt(
                id_vars=["Date"], var_name="Ação", value_name="Desempenho relativo"
            )
        )
        .mark_line()
        .encode(
            alt.X("Date:T", title="Data"),
            alt.Y("Desempenho relativo:Q").scale(zero=False),
            alt.Color("Ação:N"),
            tooltip=["Date:T", "Ação:N", "Desempenho relativo:Q"],
        )
        .properties(height=400, title="Desempenho relativo (base = 1)")
    )

""
""

"""
## Cada ação vs média das demais

O gráfico compara cada ação individualmente com a média das outras selecionadas.
"""

if len(tickers_display) <= 1:
    st.warning("Selecione 2 ou mais ações para comparar.")
    st.stop()

NUM_COLS = 4
colunas = st.columns(NUM_COLS)

for i, ticker in enumerate(tickers_display):
    if ticker not in normalizado.columns:
        continue

    peers = normalizado.drop(columns=[ticker])
    media_peers = peers.mean(axis=1)

    plot_data = pd.DataFrame({
        "Data":           normalizado.index,
        ticker:           normalizado[ticker],
        "Média das demais": media_peers,
    }).melt(id_vars=["Data"], var_name="Série", value_name="Preço")

    grafico = (
        alt.Chart(plot_data)
        .mark_line()
        .encode(
            alt.X("Data:T", title="Data"),
            alt.Y("Preço:Q").scale(zero=False),
            alt.Color(
                "Série:N",
                scale=alt.Scale(domain=[ticker, "Média das demais"], range=["#e63946", "#adb5bd"]),
                legend=alt.Legend(orient="bottom"),
            ),
            tooltip=["Data:T", "Série:N", "Preço:Q"],
        )
        .properties(title=f"{ticker} vs média", height=300)
    )

    celula = colunas[(i * 2) % NUM_COLS].container(border=True)
    celula.write("")
    celula.altair_chart(grafico, use_container_width=True)

    plot_delta = pd.DataFrame({
        "Data":  normalizado.index,
        "Delta": normalizado[ticker] - media_peers,
    })

    grafico_delta = (
        alt.Chart(plot_delta)
        .mark_area(opacity=0.7)
        .encode(
            alt.X("Data:T", title="Data"),
            alt.Y("Delta:Q").scale(zero=False),
            color=alt.condition(
                alt.datum.Delta > 0,
                alt.value("#2dc653"),
                alt.value("#e63946"),
            ),
        )
        .properties(title=f"{ticker} − média das demais", height=300)
    )

    celula2 = colunas[(i * 2 + 1) % NUM_COLS].container(border=True)
    celula2.write("")
    celula2.altair_chart(grafico_delta, use_container_width=True)

""
""

"""
## Dados brutos
"""

# Exibe preços em reais com formatação brasileira
st.dataframe(
    dados.style.format("R$ {:.2f}"),
    use_container_width=True,
)
