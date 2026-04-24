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
# CSS global (scroll horizontal + mobile)
# ============================
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

.hscroll {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 14px;
  border: 1px solid rgba(49,51,63,0.25);
  background: #0b1220;
  padding: 16px;
  max-width: 100%;
}

.hscroll-hint {
  font-size: 0.9rem;
  opacity: 0.75;
  margin-bottom: 0.4rem;
}

.hscroll.grabbable { cursor: grab; }
.hscroll.grabbing  { cursor: grabbing; }
</style>
""", unsafe_allow_html=True)

# ============================
# Funções auxiliares
# ============================
def fmt(x, nd=3):
    return f"{x:.{nd}f}".replace(".", ",")

def fmt_voltage(v):
    return f"{fmt(v,2)} V"

def fmt_current(i):
    return f"{fmt(i,3)} A" if abs(i) >= 0.1 else f"{fmt(i*1000,2)} mA"

def plotly_hscroll(fig, height=430, min_width=1400):
    fig.update_layout(width=min_width, height=height)
    html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": False}
    )

    components.html(
        f"""
        <div class="hscroll grabbable" id="plot-{id(fig)}">{html}</div>
        <script>
        (function() {{
          const el = document.getElementById("plot-{id(fig)}");
          let d=false,x=0,l=0;
          el.addEventListener("pointerdown",e=>{{d=true;x=e.clientX;l=el.scrollLeft;el.classList.add("grabbing");}});
          el.addEventListener("pointermove",e=>{{if(!d)return;el.scrollLeft=l-(e.clientX-x);}});
          el.addEventListener("pointerup",()=>{{d=false;el.classList.remove("grabbing");}});
          el.addEventListener("pointercancel",()=>{{d=false;el.classList.remove("grabbing");}});
        }})();
        </script>
        """,
        height=height + 40,
        scrolling=False
    )

# ============================
# Cabeçalho (logo corrigido)
# ============================
col_logo, col_title = st.columns([1, 3])

with col_logo:
    try:
        st.image("logo_maua.png", use_container_width=True)
    except:
        st.warning("logo_maua.png não encontrado")

with col_title:
    st.title("Simulador Fonte de Tensão – Física II")
    st.write("Comportamento não ideal de uma fonte de tensão")

st.divider()

# ============================
# Parâmetros
# ============================
st.header("Parâmetros")

c1, c2, c3 = st.columns(3)
with c1:
    epsilon = st.slider("ε (V)", 10.0, 20.0, 12.0, 0.5)
with c2:
    r_int = st.slider("r (Ω)", 0.5, 10.0, 2.0, 0.1)
with c3:
    R = st.slider("R (Ω)", 0.1, 500.0, 500.0, 1.0)

# ============================
# Cálculos
# ============================
I = epsilon / (r_int + R)
V = epsilon - r_int * I
icc = epsilon / r_int

Pg = epsilon * I
Pd = r_int * I**2
P_util = V * I

# ============================
# CIRCUITO (SVG com swipe)
# ============================
st.header("Circuito")
st.markdown('<div class="hscroll-hint">📱 Deslize para os lados</div>', unsafe_allow_html=True)

components.html(
    f"""
    <div class="hscroll grabbable">
      <svg width="1600" height="400">
        <rect x="0" y="0" width="1600" height="400" fill="#0b1220"/>
        <text x="80" y="60" fill="white" font-size="28">Fonte com resistência interna</text>
        <text x="80" y="100" fill="white" font-size="22">r = {fmt(r_int,2)} Ω</text>
        <text x="600" y="220" fill="white" font-size="26">REOSTATO</text>
        <text x="600" y="260" fill="white" font-size="22">R = {fmt(R,2)} Ω</text>
        <text x="1100" y="220" fill="white" font-size="26">I = {fmt_current(I)}</text>
        <text x="600" y="140" fill="white" font-size="22">V = {fmt_voltage(V)}</text>
      </svg>
    </div>
    """,
    height=430,
    scrolling=False
)

st.divider()

# ============================
# GRÁFICO V x I (icc corrigido)
# ============================
st.header("Gráfico – Curva característica")
st.markdown('<div class="hscroll-hint">📱 Deslize para os lados</div>', unsafe_allow_html=True)

I_line = np.linspace(0, icc, 300)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=I_line, y=V_line, mode="lines", name="V = ε − rI"))
fig1.add_trace(go.Scatter(x=[I], y=[V], mode="markers", name="Ponto de operação"))

# ✅ icc dentro do gráfico, sem sobrepor eixo
fig1.add_trace(go.Scatter(x=[icc], y=[0], mode="markers", name="Curto-circuito"))
fig1.add_annotation(
    x=icc, y=0,
    text=f"icc = {fmt(icc,3)} A",
    showarrow=True,
    arrowhead=2,
    ax=-70, ay=-60,
    bgcolor="rgba(255,255,255,0.9)"
)

fig1.update_layout(
    xaxis=dict(title="Corrente no circuito I (A)", range=[0, 45]),
    yaxis=dict(title="Tensão no circuito V (V)", range=[0, 30]),
    margin=dict(b=60)
)

plotly_hscroll(fig1)

st.divider()

# ============================
# POTÊNCIA (swipe)
# ============================
st.header("Potência")
st.markdown('<div class="hscroll-hint">📱 Deslize para os lados</div>', unsafe_allow_html=True)

I_pow = np.linspace(0, icc, 300)
P_curve = epsilon * I_pow - r_int * I_pow**2

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=I_pow, y=P_curve, mode="lines", name="Pútil"))
fig2.add_trace(go.Scatter(
    x=[I], y=[P_util],
    mode="markers+text",
    text=[f"Pútil = {fmt(P_util,3)} W"],
    textposition="top right",
    cliponaxis=False
))

fig2.update_layout(
    xaxis=dict(title="Corrente I (A)"),
    yaxis=dict(title="Potência útil (W)")
)

plotly_hscroll(fig2)

st.divider()

# ============================
# Rendimento
# ============================
st.header("Rendimento")
eta = P_util / Pg if Pg > 0 else 0
st.metric("η", f"{fmt(100*eta,2)} %")
