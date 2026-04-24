import os
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
# - (NOVO) Circuito: swipe horizontal com dedo (pan-x) + drag-to-scroll touch/mouse
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
  padding-top: 10px;
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
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 14px;
  border: 1px solid rgba(49,51,63,0.25);
  background: #0b1220;
  padding: 16px;
  max-width: 100%;

  /* >>> NOVO: torna o gesto de dedo explicitamente horizontal */
  touch-action: pan-x;
  overscroll-behavior-x: contain;

  /* evita seleção de texto durante drag */
  user-select: none;
  -webkit-user-select: none;
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
   (sem alterar o gráfico; apenas adiciona scroll no container)
   ============================ */
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
                f'<div class="logo-wrap"><img src="data:image/png;base64,{b64}" alt="logo_maua"></div>',
                unsafe_allow_html=True
            )
        except Exception:
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
# (NOVO) swipe/arrastar mais confiável no mobile:
# - touch-action: pan-x no CSS
# - JS detecta gesto horizontal e impede scroll vertical da página durante o drag
# ============================
st.header("Circuito")
st.markdown(
    '<div class="hscroll-hint">📱 No celular: arraste/deslize para os lados para ver o circuito completo.</div>',
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
  <rect class="srcBox" x="60" y="140" width="200" height="370" rx="28"/>
  <text class="textW panelText" x="160" y="188" text-anchor="middle">FONTE</text>
  <rect class="srcInner" x="95" y="215" width="130" height="78" rx="18"/>
  <text class="textW panelText2" x="160" y="265" text-anchor="middle" fill="#5eead4">{fmt_voltage(epsilon)}</text>

  <!-- Símbolo de bateria -->
  <line class="battery" x1="135" y1="320" x2="185" y2="320"/>
  <line class="battery" x1="150" y1="345" x2="170" y2="345"/>
  <line class="battery" x1="160" y1="305" x2="160" y2="360"/>

  <!-- Terminais da fonte -->
  <circle class="node" cx="260" cy="260" r="7"/>
  <circle class="node" cx="260" cy="460" r="7"/>

  <!-- REOSTATO -->
  <rect class="panel" x="620" y="220" width="380" height="100" rx="18"/>
  <text class="textW panelText" x="810" y="265" text-anchor="middle">REOSTATO</text>
  <text class="textW panelText2" x="810" y="302" text-anchor="middle">R = {fmt(R,2)} Ω</text>

  <!-- Nós do reostato -->
  <circle class="node" cx="620" cy="260" r="7"/>
  <circle class="node" cx="1000" cy="260" r="7"/>

  <!-- VOLTÍMETRO -->
  <text class="textW label" x="810" y="85" text-anchor="middle">Voltímetro</text>
  <rect class="panelPurple" x="660" y="125" width="300" height="74" rx="16" filter="url(#panelGlowPurple)"/>
  <text class="textW panelText2" x="810" y="149" text-anchor="middle">
    V<tspan dy="7" font-size="18">R</tspan><tspan dy="-7"></tspan> = {fmt_voltage(V)}
  </text>

  <!-- Fios do voltímetro -->
  <path class="wireThin" d="M 620 260 L 620 195 L 1000 195" />
  <path class="wireThin" d="M 1000 260 L 1000 195 L 920 195" />

  <!-- AMPERÍMETRO -->
  <circle class="circleA" cx="1120" cy="260" r="42" filter="url(#panelGlowGreen)"/>
  <text class="textW panelText" x="1120" y="272" text-anchor="middle">A</text>

  <!-- Painel do amperímetro -->
  <text class="textW label" x="1390" y="130" text-anchor="middle">Amperímetro</text>
  <rect class="panelGreen" x="1260" y="145" width="310" height="74" rx="16" filter="url(#panelGlowGreen)"/>
  <text class="textW panelText2" x="1415" y="193" text-anchor="middle" fill="#86efac">
    I = {fmt_current(I)}
  </text>

  <!-- FIOS PRINCIPAIS -->
  <path class="wire" d="M 260 260 L 629 261" />
  <path class="wire" d="M 1000 261 L 1078 260" />
  <path class="wire" d="M 1163 261 L 1551 261 L 1551 461 L 261 461" />

</svg>
</div>

<script>
(function() {{
  const el = document.getElementById("circuit-scroll");
  if (!el) return;

  // Estado do drag
  let isDown = false;
  let startX = 0;
  let startY = 0;
  let scrollLeft = 0;
  let lockHorizontal = false;   // só trava quando o gesto é claramente horizontal

  const getPoint = (e) => {{
    // pointer/mouse: clientX/Y direto; touch: primeiro toque
    if (e.touches && e.touches.length) {{
      return {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
    }}
    return {{ x: e.clientX, y: e.clientY }};
  }};

  const onDown = (e) => {{
    // Não interfere em links etc. (não há no SVG, mas mantém robustez)
    isDown = true;
    lockHorizontal = false;

    el.classList.add("grabbing");
    el.classList.remove("grabbable");

    const p = getPoint(e);
    startX = p.x;
    startY = p.y;
    scrollLeft = el.scrollLeft;

    // Pointer capture (quando disponível)
    if (e.pointerId !== undefined) {{
      try {{ el.setPointerCapture(e.pointerId); }} catch(err) {{}}
    }}
  }};

  const onMove = (e) => {{
    if (!isDown) return;

    const p = getPoint(e);
    const dx = p.x - startX;
    const dy = p.y - startY;

    // Decide se o usuário quer rolar horizontalmente
    if (!lockHorizontal) {{
      // se o movimento horizontal superar o vertical (com folga), trava em horizontal
      if (Math.abs(dx) > Math.abs(dy) + 6) {{
        lockHorizontal = true;
      }} else {{
        // ainda não travou: deixa a rolagem vertical normal
        return;
      }}
    }}

    // Se está em gesto horizontal: impede "scroll da página" e arrasta o container
    // IMPORTANTE: precisa de listener touchmove com passive:false
    if (e.cancelable) e.preventDefault();
    el.scrollLeft = scrollLeft - dx;
  }};

  const onUp = (e) => {{
    isDown = false;
    lockHorizontal = false;

    el.classList.remove("grabbing");
    el.classList.add("grabbable");

    if (e && e.pointerId !== undefined) {{
      try {{ el.releasePointerCapture(e.pointerId); }} catch(err) {{}}
    }}
  }};

  // Pointer events (mais moderno; cobre mouse + touch em muitos browsers)
  el.addEventListener("pointerdown", onDown);
  el.addEventListener("pointermove", onMove);
  el.addEventListener("pointerup", onUp);
  el.addEventListener("pointercancel", onUp);

  // Touch fallback (iOS/Safari às vezes funciona melhor com touch explícito)
  el.addEventListener("touchstart", onDown, {{ passive: true }});
  el.addEventListener("touchmove", onMove, {{ passive: false }});
  el.addEventListener("touchend", onUp, {{ passive: true }});
  el.addEventListener("touchcancel", onUp, {{ passive: true }});
}})();
</script>
"""

# scrolling=False mantém o iframe sem scroll próprio; o scroll está no div interno
components.html(svg_html, height=580, scrolling=False)

st.divider()

# ============================
# Gráfico: Curva característica
# (1) Corrigir sobreposição: mover anotação do icc para dentro do gráfico
# (3) CSS já permite swipe horizontal no mobile
# ============================
st.header("Gráfico")
st.subheader("Curva característica da fonte")
st.markdown(
    '<div class="hscroll-hint">📱 No celular: deslize para os lados para ver o gráfico completo.</div>',
    unsafe_allow_html=True
)

I_line = np.linspace(0, icc, 250)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=I_line, y=V_line, mode="lines",
    name="V = ε - r·I", line=dict(width=3)
))

fig1.add_trace(go.Scatter(
    x=[I], y=[V],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12, line=dict(color="white", width=1)),
    text=[f"  (I={fmt(I,3)} A, V={fmt(V,3)} V)"],
    textposition="middle right",
    cliponaxis=False
))

fig1.add_annotation(
    x=0, y=epsilon, xref="x", yref="y",
    text=f"ε = {fmt(epsilon,2)} V",
    showarrow=True, arrowhead=2, ax=60, ay=-30,
    font=dict(size=13, color="#111"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="rgba(0,0,0,0.15)", borderwidth=1
)

fig1.add_trace(go.Scatter(
    x=[icc], y=[0],
    mode="markers",
    name="Curto-circuito",
    marker=dict(color="#333", size=9),
    cliponaxis=False
))

fig1.add_annotation(
    x=icc, y=0, xref="x", yref="y",
    text=f"icc = {fmt(icc,3)} A",
    showarrow=True,
    arrowhead=2,
    ax=0, ay=-35,
    font=dict(size=13, color="#222"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="rgba(0,0,0,0.15)", borderwidth=1,
)

fig1.update_layout(
    margin=dict(l=10, r=10, t=10, b=80),
    height=430,
    xaxis=dict(title="Corrente no circuito I (A)", range=[0, float(I_AXIS_MAX_GLOBAL)], fixedrange=True),
    yaxis=dict(title="Tensão no circuito V (V)", range=[0, 30], fixedrange=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig1, use_container_width=True, theme="streamlit")
st.caption("a resistência do reostato do circuito foi alterada para obtermos diferentes valores de tensão e corrente do circuito")
st.write(f"**Para o valor atual de R:**  I = **{fmt(I,3)} A** e V = **{fmt(V,3)} V**.")

st.divider()

# ============================
# Potência
# ============================
st.header("Potência")
st.markdown(
    '<div class="hscroll-hint">📱 No celular: deslize para os lados para ver o gráfico completo.</div>',
    unsafe_allow_html=True
)

st.write("**Potência = energia por tempo (unidade Watts)**")
st.write("**A partir da equação característica:**")
st.latex(r"V\,I = \varepsilon\,I - r\,I^2")
st.latex(r"P_{\mathrm{útil}} = P_g - P_d")

I_pow = np.linspace(0, icc, 300)
P_curve = epsilon * I_pow - r_int * I_pow**2

P_max = float(np.max(P_curve)) if len(P_curve) else 0.0
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
    x=[I_opt], y=[epsilon * I_opt - r_int * I_opt**2],
    mode="markers+
