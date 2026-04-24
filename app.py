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
  width: 100%;
  touch-action: pan-y;
}

/* Mantém a largura natural do SVG para permitir scroll */
.hscroll svg {
  display: block;
  max-width: none;
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

# Curva característica: eixo x fixo
I_AXIS_MAX_GLOBAL = EPS_MAX / RINT_MIN  # 60 A

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
# Circuito (SVG limpo + sem cortes + drag-to-scroll)
# ============================
st.header("Circuito")
st.markdown(
    '<div class="hscroll-hint">💡 Dica: no celular, arraste a figura para os lados.</div>',
    unsafe_allow_html=True
)

# ATENÇÃO: f-string -> chaves literais no CSS/JS devem ser {{ e }}
svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable">
<svg width="1400" height="460" viewBox="0 0 1400 460"
     xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Circuito: fonte com resistência interna, reostato, voltímetro em paralelo e amperímetro em série">

  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#050a16"/>
      <stop offset="100%" stop-color="#0b1630"/>
    </linearGradient>

    <!-- brilho suave para fios -->
    <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="2.5" flood-color="#28d17c" flood-opacity="0.55"/>
      <feDropShadow dx="0" dy="0" stdDeviation="6.0" flood-color="#28d17c" flood-opacity="0.22"/>
    </filter>

    <filter id="panelGlowPurple" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#8b5cf6" flood-opacity="0.35"/>
    </filter>

    <filter id="panelGlowGreen" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#22c55e" flood-opacity="0.30"/>
    </filter>

    <filter id="panelGlowYellow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#f7b500" flood-opacity="0.28"/>
    </filter>

    <style>
      .bg {{ fill: url(#bg); }}

      /* fios (bem visíveis) */
      .wire {{
        stroke:#28d17c;
        stroke-width:12;
        fill:none;
        filter:url(#softGlow);
        stroke-linecap:round;
        stroke-linejoin:round;
      }}
      .wireThin {{
        stroke:#28d17c;
        stroke-width:8;
        fill:none;
        filter:url(#softGlow);
        stroke-linecap:round;
        stroke-linejoin:round;
      }}

      /* nós */
      .node {{
        fill:#28d17c;
        opacity:0.98;
        filter:url(#softGlow);
      }}

      /* textos */
      .textW {{ font-family: Arial, Helvetica, sans-serif; fill:#e8eefc; }}
      .title {{ font-size:30px; font-weight:900; }}
      .label {{ font-size:20px; font-weight:700; opacity:0.95; }}
      .small {{ font-size:17px; font-weight:650; opacity:0.92; }}

      /* caixas / componentes */
      .srcBox {{
        fill: rgba(10,16,30,0.55);
        stroke: rgba(255,255,255,0.22);
        stroke-width: 3;
      }}
      .srcInner {{
        fill: rgba(10,16,30,0.30);
        stroke: rgba(255,255,255,0.15);
        stroke-width: 2;
      }}

      .panelYellow {{
        fill: rgba(10,16,30,0.18);
        stroke:#f7b500;
        stroke-width:4;
      }}
      .panelPurple {{
        fill: rgba(10,16,30,0.55);
        stroke:#8b5cf6;
        stroke-width:3;
      }}
      .panelGreen {{
        fill: rgba(10,16,30,0.55);
        stroke:#22c55e;
        stroke-width:3;
      }}

      .meterCircle {{
        fill: rgba(10,16,30,0.60);
        stroke: rgba(255,255,255,0.22);
        stroke-width: 3;
      }}
      .meterSymbol {{ font-size:32px; font-weight:900; }}
    </style>
  </defs>

  <!-- Fundo -->
  <rect class="bg" x="0" y="0" width="1400" height="460" rx="18"/>

  <!-- =======================
       COORDENADAS (padronizadas)
       =======================
       Terminais série (linha principal): y = 240
       Retorno inferior: y = 370
       Fonte:  x ~ 70..290
       Reostato: x ~ 420..820
       Amperímetro: x ~ 980
       Painel do amperímetro: x ~ 1040..1320
  -->

  <!-- =======================
       TEXTOS (não sobrepõem)
       ======================= -->
  <text class="textW title" x="60" y="60">Fonte (ajustada em “Parâmetros”)</text>
  <text class="textW label" x="60" y="98">ε = {fmt(epsilon,2)} V</text>
  <text class="textW label" x="60" y="128">r = {fmt(r_int,2)} Ω</text>

  <!-- =======================
       FONTE (esquerda)
       ======================= -->
  <rect class="srcBox" x="80" y="155" width="210" height="245" rx="26"/>
  <text class="textW title" x="185" y="208" text-anchor="middle" font-size="26">FONTE</text>

  <rect class="srcInner" x="110" y="228" width="150" height="70" rx="16"/>
  <text class="textW label" x="185" y="272" text-anchor="middle" fill="#5eead4">ε = {fmt_voltage(epsilon)}</text>

  <!-- símbolo da bateria -->
  <line x1="145" y1="328" x2="225" y2="328" stroke="#e8eefc" stroke-width="7" stroke-linecap="round"/>
  <line x1="162" y1="362" x2="208" y2="362" stroke="#e8eefc" stroke-width="7" stroke-linecap="round"/>
  <text class="textW small" x="235" y="333">+</text>
  <text class="textW small" x="215" y="372">−</text>

  <!-- Terminais da fonte -->
  <circle class="node" cx="305" cy="240" r="7"/>
  <circle class="node" cx="305" cy="370" r="7"/>

  <!-- =======================
       REOSTATO (centro)
       ======================= -->
  <rect class="panelYellow" x="420" y="185" width="400" height="140" rx="18" filter="url(#panelGlowYellow)"/>

  <!-- Terminais do reostato -->
  <circle class="node" cx="420" cy="240" r="7"/>
  <circle class="node" cx="820" cy="240" r="7"/>

  <!-- Símbolo (zigzag) do reostato -->
  <path class="wireThin" d="
    M 420 240
    L 465 215
    L 510 265
    L 555 215
    L 600 265
    L 645 215
    L 690 265
    L 735 215
    L 780 265
    L 820 240
  " />

  <!-- seta do reostato -->
  <line x1="585" y1="182" x2="720" y2="318" stroke="#f7b500" stroke-width="7" stroke-linecap="round" filter="url(#panelGlowYellow)"/>
  <polygon points="715,318 750,322 733,293" fill="#f7b500" filter="url(#panelGlowYellow)"/>

  <!-- Texto do reostato (embaixo, sem sobrepor) -->
  <text class="textW title" x="620" y="380" text-anchor="middle">Reostato (série)</text>
  <text class="textW label" x="620" y="412" text-anchor="middle">R = {fmt(R,2)} Ω</text>

  <!-- =======================
       VOLTÍMETRO (paralelo, acima)
       ======================= -->
  <text class="textW title" x="620" y="74" text-anchor="middle">Voltímetro (paralelo)</text>

  <!-- Valor da tensão ACIMA do voltímetro (pedido) -->
  <rect class="panelPurple" x="490" y="88" width="260" height="58" rx="16" filter="url(#panelGlowPurple)"/>
  <text class="textW label" x="620" y="126" text-anchor="middle">V = {fmt_voltage(V)}</text>

  <!-- voltímetro (círculo) -->
  <circle class="meterCircle" cx="620" cy="180" r="42"/>
  <text class="textW meterSymbol" x="620" y="194" text-anchor="middle">V</text>

  <!-- =======================
       AMPERÍMETRO (direita - sem corte)
       ======================= -->
  <circle class="meterCircle" cx="980" cy="240" r="44"/>
  <text class="textW meterSymbol" x="980" y="255" text-anchor="middle">A</text>

  <text class="textW title" x="1180" y="205" text-anchor="middle">Amperímetro (série)</text>
  <rect class="panelGreen" x="1040" y="220" width="320" height="82" rx="16" filter="url(#panelGlowGreen)"/>
  <text class="textW label" x="1200" y="272" text-anchor="middle" fill="#86efac">I = {fmt_current(I)}</text>

  <!-- =======================
       FIOS (sem sobreposição / sem sumir)
       Desenhados por ÚLTIMO e em segmentos
       ======================= -->

  <!-- Série: Fonte -> Reostato -->
  <path class="wire" d="M 305 240 L 420 240" />

  <!-- Série: Reostato -> Amperímetro -->
  <path class="wire" d="M 820 240 L 936 240" />

  <!-- Série: Amperímetro -> canto direito -> retorno -->
  <path class="wire" d="M 1024 240 L 1330 240 L 1330 370" />

  <!-- Retorno inferior: canto direito -> Fonte -->
  <path class="wire" d="M 1330 370 L 305 370" />

  <!-- Paralelo do voltímetro: terminais do reostato -> voltímetro -->
  <path class="wireThin" d="M 420 240 L 420 180 L 578 180" />
  <path class="wireThin" d="M 820 240 L 820 180 L 662 180" />

  <!-- Nós para reforçar visualmente conexões -->
  <circle class="node" cx="420" cy="180" r="6"/>
  <circle class="node" cx="820" cy="180" r="6"/>
  <circle class="node" cx="1330" cy="240" r="6"/>
  <circle class="node" cx="1330" cy="370" r="6"/>

  <!-- legenda inferior -->
  <text class="textW small" x="60" y="445">
    Série: fonte → reostato → amperímetro → retorno à fonte. Paralelo: voltímetro nos terminais do reostato.
  </text>

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
    try {{ el.setPointerCapture(e.pointerId); }} catch(err) {{}}
  }};

  const move = (e) => {{
    if (!isDown) return;
    e.preventDefault();
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
  el.addEventListener("pointermove", move, {{ passive: false }});
  el.addEventListener("pointerup", up);
  el.addEventListener("pointercancel", up);
}})();
</script>
"""

components.html(svg_html, height=520, scrolling=False)

# ============================
# Gráfico: Curva característica
# ============================
st.header("Gráfico")
st.subheader("Curva característica da fonte")

I_line = np.linspace(0, icc, 250)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=I_line, y=V_line, mode="lines", name="V = ε - r·I", line=dict(width=3)))

fig1.add_trace(go.Scatter(
    x=[I], y=[V],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12),
    text=[f"  (I={fmt(I,3)} A, V={fmt(V,3)} V)"],
    textposition="middle right"
))

fig1.add_annotation(
    x=0, y=epsilon, xref="x", yref="y",
    text=f"ε = {fmt(epsilon,2)} V",
    showarrow=True, arrowhead=2, ax=60, ay=-30,
    font=dict(size=13, color="#111"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="rgba(0,0,0,0.15)", borderwidth=1
)

fig1.add_trace(go.Scatter(x=[icc], y=[0], mode="markers", name="Curto-circuito", marker=dict(color="#333", size=9)))

fig1.add_annotation(
    x=icc, xref="x",
    yref="paper", y=-0.18,
    text=f"icc = {fmt(icc,3)} A",
    showarrow=False,
    font=dict(size=13, color="#222"),
    bgcolor="rgba(255,255,255,0.85)",
    bordercolor="rgba(0,0,0,0.15)", borderwidth=1
)

fig1.update_layout(
    margin=dict(l=10, r=10, t=10, b=80),
    height=430,
    xaxis=dict(title="Corrente no circuito I (A)", range=[0, float(I_AXIS_MAX_GLOBAL)], fixedrange=True),
    yaxis=dict(title="Tensão no circuito V (V)", range=[0, 30], fixedrange=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig1, width="stretch", theme="streamlit")
st.caption("a resistência do reostato do circuito foi alterada para obtermos diferentes valores de tensão e corrente do circuito")
st.write(f"**Para o valor atual de R:**  I = **{fmt(I,3)} A** e V = **{fmt(V,3)} V**.")

st.divider()

# ============================
# Potência (eixos auto-ajustáveis)
# ============================
st.header("Potência")
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
fig2.add_trace(go.Scatter(x=I_pow, y=P_curve, mode="lines", name="Pútil(I) = εI - rI²", line=dict(width=3)))
fig2.add_trace(go.Scatter(
    x=[I], y=[P_util],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12),
    text=[f"  Pútil={fmt(P_util,3)} W"],
    textposition="middle right"
))

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
# Rendimento
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
