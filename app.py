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
# ============================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2rem; }

@media (max-width: 600px) {
  h1 { font-size: 1.45rem !important; }
  h2 { font-size: 1.15rem !important; }
  h3 { font-size: 1.02rem !important; }
}

/* Container com scroll horizontal */
.hscroll {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 14px;
  border: 1px solid rgba(49,51,63,0.25);
  background: #0b1220;
  padding: 10px;
}

/* Dica */
.hscroll-hint {
  font-size: 0.9rem;
  opacity: 0.75;
  margin: 0.1rem 0 0.6rem 0;
}

/* Cursor para drag */
.hscroll.grabbable { cursor: grab; }
.hscroll.grabbing  { cursor: grabbing; }
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
    """Mostra corrente em A ou mA para o painel do amperímetro (estilo da figura)."""
    if abs(I_amp) < 0.1:
        return f"{fmt(I_amp*1000,2)} mA"
    return f"{fmt(I_amp,3)} A"

def fmt_voltage(V):
    return f"{fmt(V,2)} V"

# ============================
# Faixas (atualizadas)
# ============================
EPS_MIN, EPS_MAX = 10.0, 30.0          # (5) epsilon mínimo 10 V + topo coerente com eixo 30V
RINT_MIN, RINT_MAX = 0.5, 10.0
RLOAD_MIN, RLOAD_MAX = 1.0, 2000.0     # amplia para permitir correntes em mA como na sua imagem

# Para manter a curva característica com eixo x fixo (não mudando a escala horizontal)
I_AXIS_MAX_GLOBAL = EPS_MAX / RINT_MIN  # 30/0.5 = 60 A

# ============================
# Início: duas colunas
# ============================
col_logo, col_title = st.columns([1, 3], vertical_alignment="center")

with col_logo:
    try:
        st.image("logo_maua.png", use_container_width=True)
    except Exception:
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
    epsilon = st.slider(
        "ε (tensão na fonte) [V]",
        min_value=float(EPS_MIN),
        max_value=float(EPS_MAX),
        value=12.0,
        step=0.5
    )

with c2:
    r_int = st.slider(
        "r (resistência interna) [Ω]",
        min_value=float(RINT_MIN),
        max_value=float(RINT_MAX),
        value=2.0,
        step=0.1
    )

with c3:
    R = st.slider(
        "R (resistência do reostato / circuito) [Ω]",
        min_value=float(RLOAD_MIN),
        max_value=float(RLOAD_MAX),
        value=1100.0,
        step=1.0
    )

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
# (1) Circuito parecido com a imagem + drag-to-scroll
# ============================
st.header("Circuito")
st.markdown('<div class="hscroll-hint">💡 Dica: no celular, arraste a figura para os lados.</div>',
            unsafe_allow_html=True)

# Estilo inspirado na imagem enviada (fundo escuro + fios verdes neon + painéis)
# Inclui JS para drag-to-scroll (mouse e touch via pointer events)
svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable">
<svg width="1500" height="420" viewBox="0 0 1500 420" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#050a16"/>
      <stop offset="100%" stop-color="#0b1630"/>
    </linearGradient>

    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#28d17c" flood-opacity="0.45"/>
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#28d17c" flood-opacity="0.25"/>
    </filter>

    <filter id="panelGlowPurple" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#8b5cf6" flood-opacity="0.35"/>
    </filter>

    <filter id="panelGlowGreen" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#22c55e" flood-opacity="0.30"/>
    </filter>

    <filter id="panelGlowYellow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#f7b500" flood-opacity="0.30"/>
    </filter>

    <style>
      .bg {{ fill: url(#bg); }}
      .wire {{ stroke:#28d17c; stroke-width:12; fill:none; filter:url(#softGlow); stroke-linecap:round; stroke-linejoin:round; }}
      .textW {{ font-family: Arial, Helvetica, sans-serif; fill:#e8eefc; }}
      .label {{ font-size:28px; font-weight:600; }}
      .small {{ font-size:22px; opacity:0.95; }}
      .panelText {{ font-size:26px; font-weight:600; }}
      .panelText2 {{ font-size:24px; }}
      .panel {{ fill: rgba(10,16,30,0.55); stroke: rgba(255,255,255,0.18); stroke-width:2; }}
      .panelPurple {{ fill: rgba(10,16,30,0.55); stroke:#8b5cf6; stroke-width:3; }}
      .panelGreen  {{ fill: rgba(10,16,30,0.55); stroke:#22c55e; stroke-width:3; }}
      .panelYellow {{ fill: rgba(10,16,30,0.55); stroke:#f7b500; stroke-width:6; }}
      .circleA {{ fill: rgba(10,16,30,0.65); stroke:#22c55e; stroke-width:4; }}
      .srcBox {{ fill: rgba(10,16,30,0.60); stroke: rgba(255,255,255,0.18); stroke-width:3; }}
      .srcInner {{ fill: rgba(10,16,30,0.35); stroke: rgba(255,255,255,0.15); stroke-width:2; }}
    </style>
  </defs>

  <!-- Fundo -->
  <rect class="bg" x="0" y="0" width="1500" height="420" rx="18"/>

  <!-- Texto: Resistência interna -->
  <text class="textW label" x="55" y="95">Resistência interna = {fmt(r_int,2)} Ω</text>

  <!-- Fonte (esquerda) -->
  <rect class="srcBox" x="55" y="145" width="170" height="210" rx="28"/>
  <text class="textW panelText" x="140" y="195" text-anchor="middle">FONTE</text>
  <rect class="srcInner" x="85" y="220" width="110" height="70" rx="18"/>
  <text class="textW panelText2" x="140" y="265" text-anchor="middle" fill="#5eead4"> {fmt_voltage(epsilon)} </text>

  <!-- Painel do voltímetro (topo) -->
  <text class="textW label" x="770" y="65" text-anchor="middle">Voltímetro</text>
  <rect class="panelPurple" x="640" y="80" width="260" height="74" rx="16" filter="url(#panelGlowPurple)"/>
  <text class="textW panelText2" x="770" y="128" text-anchor="middle">
    V<tspan dy="7" font-size="18">R</tspan><tspan dy="-7"></tspan> = {fmt_voltage(V)}
  </text>

  <!-- Reostato (centro) -->
  <rect class="panel" x="620" y="175" width="320" height="165" rx="18"/>
  <text class="textW panelText" x="780" y="220" text-anchor="middle">REOSTATO (R = {fmt(R,0)} Ω)</text>
  <rect class="panelYellow" x="650" y="245" width="260" height="80" rx="18" filter="url(#panelGlowYellow)"/>

  <!-- Amperímetro (círculo) -->
  <circle class="circleA" cx="1125" cy="255" r="38" filter="url(#panelGlowGreen)"/>
  <text class="textW panelText" x="1125" y="266" text-anchor="middle">A</text>

  <!-- Painel do amperímetro (direita) -->
  <text class="textW label" x="1320" y="205" text-anchor="middle">Amperímetro</text>
  <rect class="panelGreen" x="1235" y="220" width="250" height="74" rx="16" filter="url(#panelGlowGreen)"/>
  <text class="textW panelText2" x="1360" y="268" text-anchor="middle" fill="#86efac">
    I = {fmt_current(I)}
  </text>

  <!-- Fios (retângulo com “sobe/desce”) -->
  <!-- segmento superior: sai da fonte até reostato, passando pelo A -->
  <path class="wire" d="
    M 225 250
    L 620 250
    L 940 250
    L 1087 250
    L 150 250
  " opacity="0"/>

  <!-- fio superior real -->
  <path class="wire" d="
    M 225 250
    L 620 250
    L 940 250
    L 1087 250
    L 1470 250
  "/>

  <!-- fio inferior -->
  <path class="wire" d="
    M 140 355
    L 1470 355
  "/>

  <!-- conexão vertical na esquerda (fonte) -->
  <path class="wire" d="
    M 140 300
    L 140 355
  "/>

  <!-- conexão vertical na direita -->
  <path class="wire" d="
    M 1470 250
    L 1470 355
  "/>

</svg>
</div>

<script>
(function() {{
  const el = document.getElementById("circuit-scroll");
  if (!el) return;

  let isDown = false;
  let startX = 0;
  let scrollLeft = 0;

  const down = (e) => {{
    isDown = true;
    el.classList.add("grabbing");
    el.classList.remove("grabbable");
    startX = e.clientX;
    scrollLeft = el.scrollLeft;
    el.setPointerCapture(e.pointerId);
  }};

  const move = (e) => {{
    if (!isDown) return;
    const dx = e.clientX - startX;
    el.scrollLeft = scrollLeft - dx;
  }};

  const up = (e) => {{
    isDown = false;
    el.classList.remove("grabbing");
    el.classList.add("grabbable");
    try {{ el.releasePointerCapture(e.pointerId); }} catch(err) {{}}
  }};

  el.addEventListener("pointerdown", down);
  el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", up);
  el.addEventListener("pointercancel", up);
}})();
</script>
"""
components.html(svg_html, height=460, scrolling=False)

st.divider()

# ============================
# Gráfico: Curva característica (2)(3)(4)
# ============================
st.header("Gráfico")
st.subheader("Curva característica da fonte")

I_line = np.linspace(0, icc, 250)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=I_line, y=V_line,
    mode="lines",
    name="V = ε - r·I",
    line=dict(width=3)
))

# ponto de operação
fig1.add_trace(go.Scatter(
    x=[I], y=[V],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12),
    text=[f"  (I={fmt(I,3)} A, V={fmt(V,3)} V)"],
    textposition="middle right"
))

# anotação do epsilon (2)
fig1.add_annotation(
    x=0, y=epsilon,
    xref="x", yref="y",
    text=f"ε = {fmt(epsilon,2)} V",
    showarrow=True,
    arrowhead=2,
    ax=60, ay=-30,
    font=dict(size=13, color="#111"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="rgba(0,0,0,0.15)",
    borderwidth=1
)

# marcador do curto (em (icc,0))
fig1.add_trace(go.Scatter(
    x=[icc], y=[0],
    mode="markers",
    name="Curto-circuito",
    marker=dict(color="#333", size=9)
))

# icc abaixo do eixo x (4)
fig1.add_annotation(
    x=icc, y=0,
    xref="x", yref="paper",
    y=-0.18,
    text=f"icc = {fmt(icc,3)} A",
    showarrow=False,
    font=dict(size=13, color="#222"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="rgba(0,0,0,0.15)",
    borderwidth=1
)

# (3) eixo vertical até 30 V
fig1.update_layout(
    margin=dict(l=10, r=10, t=10, b=60),
    height=430,
    xaxis=dict(
        title="Corrente no circuito I (A)",
        range=[0, float(I_AXIS_MAX_GLOBAL)],
        fixedrange=True
    ),
    yaxis=dict(
        title="Tensão no circuito V (V)",
        range=[0, 30],
        fixedrange=True
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig1, width="stretch", theme="streamlit")

st.caption("a resistência do reostato do circuito foi alterada para obtermos diferentes valores de tensão e corrente do circuito")

st.write(
    f"**Para o valor atual de R:**  I = **{fmt(I,3)} A** e V = **{fmt(V,3)} V**."
)

st.divider()

# ============================
# Potência (6): eixos auto-ajustáveis
# ============================
st.header("Potência")

st.write("**Potência = energia por tempo (unidade Watts)**")
st.write("**A partir da equação característica:**")
st.latex(r"V\,I = \varepsilon\,I - r\,I^2")
st.latex(r"P_{\mathrm{útil}} = P_g - P_d")

I_pow = np.linspace(0, icc, 300)
P_curve = epsilon * I_pow - r_int * I_pow**2

P_max = float(np.max(P_curve)) if len(P_curve) else 0.0

# ranges automáticos (boa visualização)
xmax = max(icc * 1.05, 0.5)
ymax = max(P_max * 1.20, 1.0)

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=I_pow, y=P_curve,
    mode="lines",
    name="Pútil(I) = εI - rI²",
    line=dict(width=3)
))

fig2.add_trace(go.Scatter(
    x=[I], y=[P_util],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12),
    text=[f"  Pútil={fmt(P_util,3)} W"],
    textposition="middle right"
))

# ponto de máximo
fig2.add_trace(go.Scatter(
    x=[I_opt], y=[epsilon * I_opt - r_int * I_opt**2],
    mode="markers+text",
    name="Máximo",
    marker=dict(color="#222", size=10),
    text=["  Máx (icc/2)"],
    textposition="top left"
))

fig2.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=430,
    xaxis=dict(title="Corrente I (A)", range=[0, xmax], fixedrange=True),
    yaxis=dict(title="Potência útil Pútil (W)", range=[0, ymax], fixedrange=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig2, width="stretch", theme="streamlit")

st.write(
    f"Para **Pútil máximo**, a corrente deve ser **icc/2 = {fmt(I_opt,3)} A**, "
    f"caso onde a tensão do circuito é **ε/2 = {fmt(V_opt,3)} V**."
)

st.divider()

# ============================
# Rendimento (7): incluir equações de Pútil, Pg, Pd
# ============================
st.header("Rendimento")

st.latex(r"P_{\mathrm{útil}} = V\,I")
st.latex(r"P_g = \varepsilon\,I")
st.latex(r"P_d = r\,I^2")
st.latex(r"\eta = \dfrac{P_{\mathrm{útil}}}{P_g}")

st.write(f"Para o valor atual de **R = {fmt(R,0)} Ω**:")
st.write(
    f"- **V = {fmt(V,3)} V**\n"
    f"- **I = {fmt(I,3)} A**\n"
    f"- **Pútil = V·I = {fmt(P_util,3)} W**\n"
    f"- **Pg = ε·I = {fmt(Pg,3)} W**\n"
    f"- **Pd = r·I² = {fmt(Pd,3)} W**"
)

st.metric("Rendimento η", f"{fmt(100*eta,2)} %")
