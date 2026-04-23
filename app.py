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
    padding-top: 0.6rem;
    padding-bottom: 2rem;
}

img {
    object-fit: contain;
}

.hscroll {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 14px;
  border: 1px solid rgba(49,51,63,0.25);
  background: #0b1220;
  padding: 12px;
}

.hscroll-hint {
  font-size: 0.9rem;
  opacity: 0.75;
  margin: 0.2rem 0 0.6rem 0;
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

def fmt_voltage(V):
    return f"{fmt(V,2)} V"

def fmt_current(I):
    return f"{fmt(I,3)} A" if abs(I) >= 0.1 else f"{fmt(I*1000,2)} mA"

# ============================
# Faixas
# ============================
EPS_MIN, EPS_MAX = 10.0, 20.0
RINT_MIN, RINT_MAX = 0.5, 10.0
RLOAD_MIN, RLOAD_MAX = 0.1, 500.0

# ============================
# Cabeçalho
# ============================
col_logo, col_title = st.columns([1, 4], vertical_alignment="center")

with col_logo:
    st.image("logo_maua.png", use_container_width=True)

with col_title:
    st.title("Simulador Fonte de Tensão Física II")
    st.write("Comportamento não ideal de uma fonte real")

st.divider()

# ============================
# Parâmetros
# ============================
st.header("Parâmetros")

c1, c2, c3 = st.columns(3)
with c1:
    epsilon = st.slider("ε (V)", EPS_MIN, EPS_MAX, 12.0, 0.5)
with c2:
    r_int = st.slider("r (Ω)", RINT_MIN, RINT_MAX, 2.0, 0.1)
with c3:
    R = st.slider("R (Ω)", RLOAD_MIN, RLOAD_MAX, 500.0, 1.0)

# ============================
# Cálculos
# ============================
I = epsilon / (r_int + R)
V = epsilon - r_int * I
icc = epsilon / r_int

Pg = epsilon * I
Pd = r_int * I**2
P_util = V * I

I_opt = icc / 2

# ============================
# Circuito
# ============================
st.header("Circuito")
st.markdown('<div class="hscroll-hint">💡 Arraste horizontalmente se necessário</div>', unsafe_allow_html=True)

svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable">
<svg width="1600" height="520" viewBox="0 0 1600 520"
     xmlns="http://www.w3.org/2000/svg">

<rect x="0" y="0" width="1600" height="520" rx="22" fill="#081126"/>

<text x="60" y="90" fill="white" font-size="30">
Resistência interna = {fmt(r_int,2)} Ω
</text>

<rect x="60" y="130" width="190" height="260" rx="28"
      fill="rgba(10,16,30,0.6)" stroke="white" stroke-opacity="0.2"/>

<text x="155" y="190" fill="white" font-size="28" text-anchor="middle">FONTE</text>
<text x="155" y="250" fill="#5eead4" font-size="26" text-anchor="middle">
{fmt_voltage(epsilon)}
</text>

<text x="820" y="90" fill="white" font-size="30" text-anchor="middle">Voltímetro</text>
<rect x="680" y="110" width="280" height="80" rx="18"
      fill="rgba(90,60,160,0.4)" stroke="#a78bfa" stroke-width="3"/>
<text x="820" y="160" fill="white" font-size="26" text-anchor="middle">
V<tspan dy="6" font-size="18">R</tspan> = {fmt_voltage(V)}
</text>

<rect x="660" y="220" width="320" height="190" rx="20"
      fill="rgba(10,16,30,0.6)" stroke="white" stroke-opacity="0.2"/>
<text x="820" y="260" fill="white" font-size="28" text-anchor="middle">
REOSTATO (R = {fmt(R,1)} Ω)
</text>

<circle cx="1160" cy="310" r="42"
        fill="rgba(10,16,30,0.7)" stroke="#22c55e" stroke-width="5"/>
<text x="1160" y="320" fill="white" font-size="28" text-anchor="middle">A</text>

<rect x="1240" y="270" width="280" height="80" rx="18"
      fill="rgba(10,60,40,0.5)" stroke="#22c55e" stroke-width="3"/>
<text x="1380" y="320" fill="#86efac" font-size="26" text-anchor="middle">
I = {fmt_current(I)}
</text>

<!-- FIOS -->
<path d="M 250 310 L 1520 310" stroke="#28d17c" stroke-width="12" fill="none"/>
<path d="M 155 390 L 1520 390" stroke="#28d17c" stroke-width="12" fill="none"/>
<path d="M 155 310 L 155 390" stroke="#28d17c" stroke-width="12" fill="none"/>
<path d="M 1520 310 L 1520 390" stroke="#28d17c" stroke-width="12" fill="none"/>

</svg>
</div>
"""

components.html(svg_html, height=560, scrolling=False)

st.divider()

# ============================
# Gráfico V x I
# ============================
st.header("Curva V × I")

I_line = np.linspace(0, 45, 300)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=I_line, y=V_line, mode="lines", line=dict(width=3)))

fig1.add_annotation(
    x=I/45, y=V/30,
    xref="paper", yref="paper",
    text=f"I = {fmt(I,3)} A<br>V = {fmt(V,3)} V",
    showarrow=True,
    arrowhead=3,
    bgcolor="white",
    layer="above"
)

fig1.update_layout(
    height=420,
    xaxis=dict(title="Corrente I (A)", range=[0, 45]),
    yaxis=dict(title="Tensão V (V)", range=[0, 30]),
    margin=dict(r=40)
)

st.plotly_chart(fig1, use_container_width=True)

# ============================
# Potência
# ============================
st.header("Potência")

st.latex(r"P_{\text{útil}} = P_g - P_d")

I_pow = np.linspace(0, icc, 400)
P_curve = epsilon*I_pow - r_int*I_pow**2

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=I_pow, y=P_curve, mode="lines", line=dict(width=3)))

fig2.add_annotation(
    x=I/icc, y=P_util/np.max(P_curve),
    xref="paper", yref="paper",
    text=f"P$_{{\\text{{útil}}}}$ = {fmt(P_util,3)} W",
    showarrow=True,
    arrowhead=3,
    bgcolor="white",
    layer="above"
)

fig2.update_layout(
    height=420,
    xaxis=dict(title="Corrente I (A)"),
    yaxis=dict(title="Potência útil P₍útil₎ (W)"),
    margin=dict(r=50)
)

st.plotly_chart(fig2, use_container_width=True)
``
