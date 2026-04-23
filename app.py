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
# CSS
# ============================
st.markdown("""
<style>
.block-container {
  padding-top: 0.2rem;   /* evita corte do logo */
  padding-bottom: 2rem;
}

@media (max-width: 600px) {
  h1 { font-size: 1.45rem !important; }
  h2 { font-size: 1.15rem !important; }
  h3 { font-size: 1.02rem !important; }
}

.hscroll {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 14px;
  border: 1px solid rgba(49,51,63,0.25);
  background: #0b1220;
  padding: 10px;
}

.hscroll-hint {
  font-size: 0.9rem;
  opacity: 0.75;
  margin: 0.1rem 0 0.6rem 0;
}

.hscroll.grabbable { cursor: grab; }
.hscroll.grabbing  { cursor: grabbing; }
</style>
""", unsafe_allow_html=True)

# ============================
# Helpers
# ============================
def fmt(x, nd=3):
    return f"{x:.{nd}f}".replace(".", ",")

def fmt_current(I):
    if abs(I) < 0.1:
        return f"{fmt(I*1000,2)} mA"
    return f"{fmt(I,3)} A"

def fmt_voltage(V):
    return f"{fmt(V,2)} V"

# ============================
# Faixas
# ============================
EPS_MIN, EPS_MAX = 10.0, 20.0
RINT_MIN, RINT_MAX = 0.5, 10.0
RLOAD_MIN, RLOAD_MAX = 0.1, 500.0

# ============================
# Cabeçalho
# ============================
col_logo, col_title = st.columns([1, 3], vertical_alignment="center")

with col_logo:
    st.image("logo_maua.png", use_container_width=True)

with col_title:
    st.title("Simulador Fonte de Tensão Física II")
    st.write("Veja o comportamento não ideal de uma fonte de tensão")

st.divider()

# ============================
# Equação
# ============================
st.header("Equação característica")
st.latex(r"V = \varepsilon - r\,I")

st.divider()

# ============================
# Parâmetros
# ============================
st.header("Parâmetros")
c1, c2, c3 = st.columns(3)

with c1:
    epsilon = st.slider("ε (tensão na fonte) [V]", EPS_MIN, EPS_MAX, 12.0, 0.5)

with c2:
    r_int = st.slider("r (resistência interna) [Ω]", RINT_MIN, RINT_MAX, 2.0, 0.1)

with c3:
    R = st.slider("R (resistência do reostato / circuito) [Ω]", RLOAD_MIN, RLOAD_MAX, 500.0, 1.0)

# ============================
# Cálculos
# ============================
I = epsilon / (r_int + R)
V = epsilon - r_int * I
icc = epsilon / r_int

Pg = epsilon * I
Pd = r_int * I**2
P_util = V * I
eta = P_util / Pg if Pg > 0 else 0

I_opt = icc / 2
V_opt = epsilon / 2

st.divider()

# ============================
# Circuito
# ============================
st.header("Circuito")
st.markdown('<div class="hscroll-hint">💡 Dica: no celular, arraste a figura para os lados.</div>', unsafe_allow_html=True)

svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable">
<svg width="1500" height="480" viewBox="0 0 1500 480" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="1500" height="480" rx="18" fill="#0b1630"/>

  <text x="55" y="95" fill="#e8eefc" font-size="28">
    Resistência interna = {fmt(r_int,2)} Ω
  </text>

  <text x="780" y="220" fill="#e8eefc" font-size="26" text-anchor="middle">
    REOSTATO (R = {fmt(R,1)} Ω)
  </text>

  <!-- fios -->
  <path d="M 225 260 L 1470 260" stroke="#28d17c" stroke-width="12" fill="none"/>
  <path d="M 140 380 L 1470 380" stroke="#28d17c" stroke-width="12" fill="none"/>
  <path d="M 140 320 L 140 380" stroke="#28d17c" stroke-width="12" fill="none"/>
  <path d="M 1470 260 L 1470 380" stroke="#28d17c" stroke-width="12" fill="none"/>
</svg>
</div>
"""
components.html(svg_html, height=520, scrolling=False)

st.divider()

# ============================
# Gráfico V x I
# ============================
st.header("Gráfico")
st.subheader("Curva característica da fonte")

I_line = np.linspace(0, icc, 300)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=I_line, y=V_line, mode="lines", name="V = ε − rI"))

fig1.add_annotation(
    x=I, y=V,
    text=f"I={fmt(I,3)} A<br>V={fmt(V,3)} V",
    showarrow=True,
    ax=40, ay=-40,
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="black",
    layer="above"
)

fig1.update_layout(
    height=430,
    xaxis=dict(title="Corrente I (A)", range=[0, 45], fixedrange=True),
    yaxis=dict(title="Tensão V (V)", range=[0, 30], fixedrange=True)
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ============================
# Potência
# ============================
st.header("Potência")
st.latex(r"P_{\mathrm{útil}} = P_g - P_d")

I_pow = np.linspace(0, icc, 300)
P_curve = epsilon * I_pow - r_int * I_pow**2

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=I_pow, y=P_curve, mode="lines", name=r"$P_{\mathrm{útil}}(I)$"))

fig2.add_annotation(
    x=I, y=P_util,
    text=f"P<sub>útil</sub> = {fmt(P_util,3)} W",
    showarrow=True,
    ax=50, ay=-30,
    bgcolor="rgba(255,255,255,0.95)",
    bordercolor="black",
    layer="above"
)

fig2.update_layout(
    height=430,
    xaxis=dict(title="Corrente I (A)", fixedrange=True),
    yaxis=dict(title=r"Potência útil $P_{\mathrm{útil}}$ (W)", fixedrange=True)
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============================
# Rendimento
# ============================
st.header("Rendimento")
st.latex(r"\eta = \dfrac{P_{\mathrm{útil}}}{P_g}")

st.metric("Rendimento η", f"{fmt(100*eta,2)} %")
