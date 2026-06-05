import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(
    page_title="Monitor B3",
    page_icon="📈",
    layout="wide",
)

# ─── CSS customizado ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.main {
    background-color: #0a0f1e;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Hero */
.hero-wrapper {
    background: linear-gradient(135deg, #0d1b2a 0%, #0a0f1e 50%, #091120 100%);
    border: 1px solid #1e2d40;
    border-radius: 16px;
    padding: 3rem 3.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,200,120,0.07) 0%, transparent 70%);
    pointer-events: none;
}

.hero-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    color: #00c878;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    color: #f0f4f8;
    margin-bottom: 0.75rem;
}

.hero-title span {
    color: #00c878;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #6b7f95;
    max-width: 520px;
    line-height: 1.6;
}

/* Cards de navegação */
.nav-card {
    background: #0d1b2a;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    height: 100%;
    transition: border-color 0.2s, transform 0.2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.nav-card:hover {
    border-color: #00c878;
    transform: translateY(-3px);
}

.nav-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00c878, transparent);
    opacity: 0;
    transition: opacity 0.2s;
}

.nav-card:hover::after { opacity: 1; }

.nav-icon {
    font-size: 1.8rem;
    margin-bottom: 0.75rem;
}

.nav-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8f0f8;
    margin-bottom: 0.4rem;
}

.nav-desc {
    font-size: 0.85rem;
    color: #5a7080;
    line-height: 1.5;
}

/* Métricas de mercado */
.metric-card {
    background: #0d1b2a;
    border: 1px solid #1e2d40;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    text-align: center;
}

.metric-ticker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #00c878;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}

.metric-price {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8f0f8;
}

.metric-var-pos { color: #00c878; font-size: 0.85rem; }
.metric-var-neg { color: #f45b69; font-size: 0.85rem; }

/* Rodapé */
.footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #2a3d50;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


# ─── Hero ──────────────────────────────────────────────────────────────────────
hora = datetime.now().strftime("%d/%m/%Y  %H:%M")

st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-tag">⬤ &nbsp;Painel ao vivo — {hora}</div>
    <div class="hero-title">Monitor de Ações<br><span>B3</span></div>
    <div class="hero-subtitle">
        Acompanhe cotações, compare desempenho e receba alertas
        de preço diretamente no seu WhatsApp.
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Pulso de mercado (5 ações rápidas) ───────────────────────────────────────
PULSO = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "BBDC4.SA"]

with st.spinner("Carregando pulso do mercado..."):
    try:
        tickers_obj = yf.Tickers(" ".join(PULSO))
        hist = tickers_obj.history(period="2d")["Close"]

        cols_m = st.columns(len(PULSO))
        for i, ticker in enumerate(PULSO):
            nome = ticker.replace(".SA", "")
            try:
                preco_hoje = hist[ticker].iloc[-1]
                preco_ontem = hist[ticker].iloc[-2]
                variacao = ((preco_hoje - preco_ontem) / preco_ontem) * 100
                sinal = "▲" if variacao >= 0 else "▼"
                classe_var = "metric-var-pos" if variacao >= 0 else "metric-var-neg"

                cols_m[i].markdown(f"""
                <div class="metric-card">
                    <div class="metric-ticker">{nome}</div>
                    <div class="metric-price">R$ {preco_hoje:.2f}</div>
                    <div class="{classe_var}">{sinal} {abs(variacao):.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                cols_m[i].markdown(f"""
                <div class="metric-card">
                    <div class="metric-ticker">{nome}</div>
                    <div class="metric-price">—</div>
                </div>
                """, unsafe_allow_html=True)
    except Exception:
        st.warning("Não foi possível carregar o pulso do mercado agora.")

st.markdown("<br>", unsafe_allow_html=True)


# ─── Cards de navegação ────────────────────────────────────────────────────────
st.markdown("### Navegue pelo painel")
st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">📊</div>
        <div class="nav-title">Dashboard B3</div>
        <div class="nav-desc">
            Compare o desempenho relativo entre ações,
            veja máximas, mínimas e análise de peers.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Dashboard_B3.py", label="Abrir Dashboard →", use_container_width=True)

with c2:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">🔔</div>
        <div class="nav-title">Monitor de Alertas</div>
        <div class="nav-desc">
            Defina preços de alerta para até 10 ações
            e receba notificações via WhatsApp.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Monitor_Alertas.py", label="Abrir Monitor →", use_container_width=True)

with c3:
    st.markdown("""
    <div class="nav-card">
        <div class="nav-icon">📉</div>
        <div class="nav-title">Análise Técnica</div>
        <div class="nav-desc">
            Médias móveis SMA20/SMA60, RSI e
            indicadores para embasar suas decisões.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Analise_Tecnica.py", label="Abrir Análise →", use_container_width=True)


# ─── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    MONITOR B3 &nbsp;·&nbsp; DADOS VIA YAHOO FINANCE &nbsp;·&nbsp;
    USO EXCLUSIVAMENTE INFORMATIVO — NÃO CONSTITUI RECOMENDAÇÃO DE INVESTIMENTO
</div>
""", unsafe_allow_html=True)
