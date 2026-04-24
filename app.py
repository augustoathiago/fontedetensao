import os {
    min-width: 920px;  /* força haver “lado a lado” para deslizar */
  }
}
</style>
""", unsafe_allow_html=True)

# ============================
# Helpers de formatação (pt-BR)
# ============================
def fmt(x, nd=3):
    try:
        s = f"{x:.{nd}f}"
    except Exception:
        s = str(x)
    return s.replace(".", ",")

def fmt_current(I_amp):
    """Mostra corrente em A ou mA para o painel do amperímetro."""
    if abs(I_amp) < 0.1:
        return f"{fmt(I_amp*1000,2)} mA"
    return f"{fmt(I_amp,3)} A"

def fmt_voltage(V):
    return f"{fmt(V,2)} V"

# ============================
# Faixas (atualizadas)
# ============================
EPS_MIN, EPS_MAX = 10.0, 20.0
RINT_MIN, RINT_MAX = 0.5, 10.0
RLOAD_MIN, RLOAD_MAX = 0.1, 500.0

# ============================
# Curva característica
# eixo x até 45 A
# ============================
I_AXIS_MAX_GLOBAL = 45.0

# ============================
# Início: duas colunas
# ============================
col_logo, col_title = st.columns([1, 3], vertical_alignment="center")

with col_logo:
    # (2) Renderização do logo via HTML para evitar corte no topo
    logo_path = "logo_maua.png"
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(
                f"""
                <div class="logo-wrap">
                  <img src="data:image/png;base64,{b64}" alt="Logo Mauá"/>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            # fallback
            st.image(logo_path, use_container_width=True)
    else:
        st.warning("Arquivo logo_maua.png não encontrado no diretório do app.")

with col_title:
    st.title("Simulador Fonte de Tensão Física II")
    st.write("Veja o comportamento não ideal de uma fonte de tensão")

st.divider()

# ============================
# Seção: Equação característica
# ============================
st.header("Equação característica")
st.latex(r"V = \varepsilon - r\,I")
st.write(
    "**V** é a tensão no circuito (V), **ε** é a tensão na fonte (V) (ou força eletromotriz), "
    "**r** é a resistência interna da fonte (Ω) e **I** é a corrente no circuito (A)."
)

st.divider()

# ============================
# Seção: Parâmetros
# ============================
st.header("Parâmetros")
c1, c2, c3 = st.columns(3)

with c1:
    epsilon = st.slider("ε (tensão na fonte) [V]", float(EPS_MIN), float(EPS_MAX), 12.0, 0.5)

with c2:
    r_int = st.slider("r (resistência interna) [Ω]", float(RINT_MIN), float(RINT_MAX), 2.0, 0.1)

with c3:
    R = st.slider("R (resistência do reostato / circuito) [Ω]", float(RLOAD_MIN), float(RLOAD_MAX), 500.0, 1.0)

# ============================
# Cálculos
# ============================
I = epsilon / (r_int + R)
V = epsilon - r_int * I
icc = epsilon / r_int

Pg = epsilon * I
Pd = r_int * I**2
P_util = V * I
eta = (P_util / Pg) if Pg > 0 else 0.0

I_opt = icc / 2.0
V_opt = epsilon / 2.0

st.divider()

# ============================
# Circuito
# (3) Scroll no mobile: hscroll + touch fallback + iframe scrolling=True
# ============================
st.header("Circuito")
st.markdown(
    '<div class="hscroll-hint">📱 No celular: deslize para os lados para ver o circuito completo.</div>',
    unsafe_allow_html=True
)

svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable" aria-label="Circuito com rolagem horizontal">
<svg width="1600" height="520" viewBox="-70 -70 1740 660"
     xmlns="http://www.w3.org/2000/svg"
     preserveAspectRatio="xMinYMin meet"
     style="overflow: visible;">

  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#050a16"/>
      <stop offset="100%" stop-color="#0b1630"/>
    </linearGradient>

    <filter id="softGlow" x="-35%" y="-35%" width="170%" height="170%">
      <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#28d17c" flood-opacity="0.45"/>
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#28d17c" flood-opacity="0.25"/>
    </filter>

    <filter id="panelGlowPurple" x="-35%" y="-35%" width="170%" height="170%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#8b5cf6" flood-opacity="0.35"/>
    </filter>

    <filter id="panelGlowGreen" x="-35%" y="-35%" width="170%" height="170%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#22c55e" flood-opacity="0.30"/>
    </filter>

    <style>
      .bg {{ fill: url(#bg); }}
      .wire {{
        stroke:#28d17c; stroke-width:12; fill:none;
        filter:url(#softGlow);
        stroke-linecap:round; stroke-linejoin:round;
      }}
      .wireThin {{
        stroke:#a78bfa; stroke-width:8; fill:none;
        filter:url(#panelGlowPurple);
        stroke-linecap:round; stroke-linejoin:round;
        opacity:0.95;
      }}
      .node {{ fill:#28d17c; opacity:0.95; }}
      .textW {{ font-family: Arial, Helvetica, sans-serif; fill:#e8eefc; }}
      .label {{ font-size:28px; font-weight:700; }}
      .small {{ font-size:22px; opacity:0.95; }}
      .panelText {{ font-size:26px; font-weight:700; }}
      .panelText2 {{ font-size:24px; font-weight:600; }}
      .panel {{ fill: rgba(10,16,30,0.55); stroke: rgba(255,255,255,0.18); stroke-width:2; }}
      .panelPurple {{ fill: rgba(10,16,30,0.55); stroke:#8b5cf6; stroke-width:3; }}
      .panelGreen  {{ fill: rgba(10,16,30,0.55); stroke:#22c55e; stroke-width:3; }}
      .circleA {{ fill: rgba(10,16,30,0.65); stroke:#22c55e; stroke-width:4; }}
      .srcBox {{ fill: rgba(10,16,30,0.60); stroke: rgba(255,255,255,0.20); stroke-width:3; }}
      .srcInner {{ fill: rgba(10,16,30,0.35); stroke: rgba(255,255,255,0.15); stroke-width:2; }}
      .battery {{ stroke:#e8eefc; stroke-width:4; fill:none; opacity:0.9; stroke-linecap:round; }}
    </style>
  </defs>

  <!-- Fundo -->
  <rect class="bg" x="-45" y="-45" width="1690" height="610" rx="22"/>

  <!-- Cabeçalho -->
  <text class="textW label" x="60" y="40">Fonte com resistência interna</text>
  <text class="textW small" x="60" y="78">r = {fmt(r_int,2)} Ω</text>

  <!-- BLOCO FONTE -->
  <rect class="srcBox" x="60" y="140" width="200" height="
import base64
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

# ============================
# Configuração da página
# ============================
st.set_page_config(
    page_title="Simulador Fonte de Tensão Física II",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# CSS (mobile-friendly + drag-to-scroll)
# - (2) logo: evita corte no topo
# - (3) plotly em mobile: container com scroll horizontal (swipe)
# - (3) circuito: hscroll com touch-action pan-x
# ============================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2rem; }

@media (max-width: 600px) {
  h1 { font-size: 1.45rem !important; }
  h2 { font-size: 1.15rem !important; }
  h3 { font-size: 1.02rem !important; }
}

/* ============================
   (2) Logo: não cortar no topo
   ============================ */
.logo-wrap{
  width: 100%;
  padding-top: 10px;   /* respiro no topo */
  padding-bottom: 4px;
  overflow: visible;
}
.logo-wrap img{
  width: 100%;
  height: auto;
  display: block;
  object-fit: contain;
  object-position: top center;
}

/* ============================
   Container com scroll horizontal (mobile swipe)
   ============================ */
.hscroll {
  overflow-x: scroll;              /* scroll garantido */
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;             /* essencial p/ swipe horizontal */
  overscroll-behavior-x: contain;  /* evita a página “roubar” o gesto */
  border-radius: 14px;
  border: 1px solid rgba(49,51,63,0.25);
  background: #0b1220;
  padding: 16px;
  max-width: 100%;
}

/* força scroll em telas pequenas e evita encolher demais */
.hscroll svg {
  display: block;
  min-width: 1600px;
  height: auto;
}

/* Dica */
.hscroll-hint {
  font-size: 0.9rem;
  opacity: 0.75;
  margin: 0.1rem 0 0.6rem 0;
}

/* Cursor para drag (desktop) */
.hscroll.grabbable { cursor: grab; }
.hscroll.grabbing  { cursor: grabbing; }

/* ============================
   (3) Plotly: permitir swipe horizontal no celular
   (sem alterar o gráfico; só adiciona scroll no container)
   ============================ */
@media (max-width: 900px) {
  div[data-testid="stPlotlyChart"] > div {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    -webkit-overflow-scrolling: touch !important;
  }
  div[data-testid="stPlotlyChart"] .js-plotly-plot,
