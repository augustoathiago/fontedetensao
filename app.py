import os
import base64
import numpy as np
import streamlit as st
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
# CSS global
# ============================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

@media (max-width: 600px) {
    h1 { font-size: 1.45rem !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1.02rem !important; }
}

.logo-wrap{
    width:100%;
    padding-top:10px;
    padding-bottom:4px;
}

.logo-wrap img{
    width:100%;
    height:auto;
    display:block;
    object-fit:contain;
}

.hscroll-hint {
    font-size:0.9rem;
    opacity:0.75;
    margin-bottom:0.6rem;
}

/* Scroll horizontal Plotly no mobile */
@media (max-width: 900px) {
  div[data-testid="stPlotlyChart"] > div {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    -webkit-overflow-scrolling: touch !important;
  }

  div[data-testid="stPlotlyChart"] .js-plotly-plot,
  div[data-testid="stPlotlyChart"] .plot-container.plotly {
    min-width: 920px;
  }
}
</style>
""", unsafe_allow_html=True)

# ============================
# Helpers
# ============================
def fmt(x, nd=3):
    try:
        s = f"{x:.{nd}f}"
    except Exception:
        s = str(x)
    return s.replace(".", ",")

def fmt_current(I_amp):
    if abs(I_amp) < 0.1:
        return f"{fmt(I_amp*1000,2)} mA"
    return f"{fmt(I_amp,3)} A"

def fmt_voltage(V):
    return f"{fmt(V,2)} V"

# ============================
# Limites
# ============================
EPS_MIN, EPS_MAX = 10.0, 20.0
RINT_MIN, RINT_MAX = 0.5, 10.0
RLOAD_MIN, RLOAD_MAX = 0.1, 500.0
I_AXIS_MAX_GLOBAL = 45.0

# ============================
# Cabeçalho
# ============================
col_logo, col_title = st.columns([1,3], vertical_alignment="center")

with col_logo:
    logo_path = "logo_maua.png"
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            st.markdown(
                f'<div class="logo-wrap"><img src="data:image/png;base64,{b64}"></div>',
                unsafe_allow_html=True
            )
        except:
            st.image(logo_path, use_container_width=True)

with col_title:
    st.title("Simulador Fonte de Tensão Física II")
    st.write("Veja o comportamento não ideal de uma fonte de tensão")

st.divider()

# ============================
# Equação
# ============================
st.header("Equação característica")
st.latex(r"V = \varepsilon - rI")

st.write(
    "**V** é a tensão no circuito (V), **ε** é a tensão da fonte (V), "
    "**r** é a resistência interna (Ω) e **I** é a corrente (A)."
)

st.divider()

# ============================
# Parâmetros
# ============================
st.header("Parâmetros")

c1, c2, c3 = st.columns(3)

with c1:
    epsilon = st.slider("ε (tensão da fonte) [V]", EPS_MIN, EPS_MAX, 12.0, 0.5)

with c2:
    r_int = st.slider("r (resistência interna) [Ω]", RINT_MIN, RINT_MAX, 2.0, 0.1)

with c3:
    R = st.slider("R (reostato) [Ω]", RLOAD_MIN, RLOAD_MAX, 500.0, 1.0)

# ============================
# Cálculos
# ============================
I = epsilon / (r_int + R)
V = epsilon - r_int * I
icc = epsilon / r_int

Pg = epsilon * I
Pd = r_int * I**2
P_util = V * I
eta = (P_util / Pg) if Pg > 0 else 0

I_opt = icc / 2
V_opt = epsilon / 2

st.divider()

# ============================
# Circuito
# ============================
st.header("Circuito")

st.markdown("""
<style>
.circuit-wrapper {
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    border-radius: 14px;
    border: 1px solid rgba(49,51,63,0.25);
    background: #0b1220;
    padding: 10px;
    margin-bottom: 10px;
}

.circuit-inner {
    width: 1600px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hscroll-hint">📱 No celular: deslize para os lados para ver o circuito completo.</div>',
    unsafe_allow_html=True
)

svg_html = f"""
<div class="circuit-wrapper">
  <div class="circuit-inner">

<svg width="1600" height="520" viewBox="-70 -70 1740 660"
     xmlns="http://www.w3.org/2000/svg"
     preserveAspectRatio="xMinYMin meet"
     style="display:block;">

  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#050a16"/>
      <stop offset="100%" stop-color="#0b1630"/>
    </linearGradient>

    <style>
      .bg {{ fill:url(#bg); }}
      .wire {{
        stroke:#28d17c;
        stroke-width:12;
        fill:none;
        stroke-linecap:round;
      }}
      .textW {{ fill:#e8eefc; font-family:Arial; }}
      .node {{ fill:#28d17c; }}
    </style>
  </defs>

  <rect class="bg" x="-45" y="-45" width="1690" height="610" rx="22"/>

  <text class="textW" x="60" y="40" font-size="28" font-weight="700">
    Fonte com resistência interna
  </text>

  <text class="textW" x="60" y="78" font-size="22">
    r = {fmt(r_int,2)} Ω
  </text>

  <rect x="60" y="140" width="200" height="370" rx="28"
        fill="rgba(10,16,30,0.6)"
        stroke="rgba(255,255,255,0.2)"
        stroke-width="3"/>

  <text class="textW" x="160" y="190" text-anchor="middle" font-size="26" font-weight="700">
    FONTE
  </text>

  <text class="textW" x="160" y="260" text-anchor="middle" font-size="24">
    {fmt_voltage(epsilon)}
  </text>

  <circle class="node" cx="260" cy="260" r="7"/>
  <circle class="node" cx="260" cy="460" r="7"/>

  <rect x="620" y="220" width="380" height="100" rx="18"
        fill="rgba(10,16,30,0.55)"
        stroke="rgba(255,255,255,0.2)"
        stroke-width="2"/>

  <text class="textW" x="810" y="265" text-anchor="middle" font-size="26" font-weight="700">
    REOSTATO
  </text>

  <text class="textW" x="810" y="300" text-anchor="middle" font-size="22">
    R = {fmt(R,2)} Ω
  </text>

  <circle cx="1120" cy="260" r="42"
          fill="rgba(10,16,30,0.65)"
          stroke="#22c55e"
          stroke-width="4"/>

  <text class="textW" x="1120" y="272" text-anchor="middle" font-size="28" font-weight="700">
    A
  </text>

  <text class="textW" x="1415" y="193" text-anchor="middle" font-size="22">
    I = {fmt_current(I)}
  </text>

  <path class="wire" d="M 260 260 L 620 260"/>
  <path class="wire" d="M 1000 260 L 1080 260"/>
  <path class="wire" d="M 1163 261 L 1551 261 L 1551 461 L 261 461"/>

</svg>

  </div>
</div>
"""

st.markdown(svg_html, unsafe_allow_html=True)

st.divider()

# ============================
# Gráfico
# ============================
st.header("Gráfico")

I_line = np.linspace(0, icc, 250)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=I_line,
    y=V_line,
    mode="lines",
    name="V = ε - rI"
))

fig1.add_trace(go.Scatter(
    x=[I],
    y=[V],
    mode="markers",
    marker=dict(size=12)
))

fig1.update_layout(
    height=430,
    xaxis=dict(title="Corrente I (A)", range=[0, I_AXIS_MAX_GLOBAL]),
    yaxis=dict(title="Tensão V (V)")
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ============================
# Potência
# ============================
st.header("Potência")

I_pow = np.linspace(0, icc, 300)
P_curve = epsilon * I_pow - r_int * I_pow**2

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=I_pow,
    y=P_curve,
    mode="lines",
    name="Pútil"
))

fig2.update_layout(
    height=430,
    xaxis=dict(title="Corrente I (A)"),
    yaxis=dict(title="Potência (W)")
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============================
# Rendimento
# ============================
st.header("Rendimento")

st.metric("Rendimento η", f"{fmt(eta*100,2)} %")

st.write(
    f"**V = {fmt(V,3)} V**  \n"
    f"**I = {fmt(I,3)} A**  \n"
    f"**Pútil = {fmt(P_util,3)} W**  \n"
    f"**Pg = {fmt(Pg,3)} W**  \n"
    f"**Pd = {fmt(Pd,3)} W**"
)
```

Esse código já inclui a correção do scroll horizontal para Android Chrome usando `st.markdown()` em vez de `components.html()`.
