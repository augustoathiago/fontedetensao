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
# Circuito (SVG corrigido) + drag-to-scroll
# ============================
st.header("Circuito")
st.markdown('<div class="hscroll-hint">💡 Dica: no celular, arraste a figura para os lados.</div>', unsafe_allow_html=True)

# IMPORTANTE: é f-string -> chaves literais do CSS/JS precisam ser {{ e }}
svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable">
<svg width="1900" height="540" viewBox="0 0 1900 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Circuito elétrico com fonte, reostato, voltímetro e amperímetro">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#050a16"/>
      <stop offset="100%" stop-color="#0b1630"/>
    </linearGradient>

    <filter id="softGlow" x="-25%" y="-25%" width="150%" height="150%">
      <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#28d17c" flood-opacity="0.45"/>
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#28d17c" flood-opacity="0.25"/>
    </filter>

    <filter id="panelGlowPurple" x="-25%" y="-25%" width="150%" height="150%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#8b5cf6" flood-opacity="0.35"/>
    </filter>

    <filter id="panelGlowGreen" x="-25%" y="-25%" width="150%" height="150%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#22c55e" flood-opacity="0.30"/>
    </filter>

    <filter id="panelGlowYellow" x="-25%" y="-25%" width="150%" height="150%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#f7b500" flood-opacity="0.30"/>
    </filter>

    <style>
      .bg {{ fill: url(#bg); }}
      .wire {{
        stroke:#28d17c; stroke-width:12; fill:none;
        filter:url(#softGlow);
        stroke-linecap:round; stroke-linejoin:round;
      }}
      .wireThin {{
        stroke:#28d17c; stroke-width:8; fill:none;
        filter:url(#softGlow);
        stroke-linecap:round; stroke-linejoin:round;
      }}
      .node {{ fill:#28d17c; opacity:0.95; filter:url(#softGlow); }}
      .textW {{ font-family: Arial, Helvetica, sans-serif; fill:#e8eefc; }}
      .label {{ font-size:30px; font-weight:800; }}
      .subLabel {{ font-size:22px; opacity:0.95; font-weight:600; }}
      .panelText2 {{ font-size:22px; font-weight:750; }}
      .panelPurple {{
        fill: rgba(10,16,30,0.60);
        stroke:#8b5cf6;
        stroke-width:3;
      }}
      .panelGreen {{
        fill: rgba(10,16,30,0.60);
        stroke:#22c55e;
        stroke-width:3;
      }}
      .panelYellow {{
        fill: rgba(10,16,30,0.35);
        stroke:#f7b500;
        stroke-width:4;
      }}
      .meterCircle {{
        fill: rgba(10,16,30,0.65);
        stroke: rgba(255,255,255,0.22);
        stroke-width: 3;
      }}
      .meterSymbol {{ font-size:34px; font-weight:900; }}
      .srcBox {{
        fill: rgba(10,16,30,0.60);
        stroke: rgba(255,255,255,0.18);
        stroke-width:3;
      }}
      .srcInner {{
        fill: rgba(10,16,30,0.35);
        stroke: rgba(255,255,255,0.15);
        stroke-width:2;
      }}
      .tiny {{ font-size:18px; opacity:0.9; font-weight:600; }}
    </style>
  </defs>

  <!-- Fundo -->
  <rect class="bg" x="0" y="0" width="1900" height="540" rx="18"/>

  <!-- =======================
       Componentes (primeiro)
       ======================= -->

  <!-- Fonte (esquerda) -->
  <text class="textW label" x="70" y="70">Fonte (ajustada em “Parâmetros”)</text>
  <text class="textW subLabel" x="70" y="110">ε = {fmt(epsilon,2)} V</text>
  <text class="textW subLabel" x="70" y="145">r = {fmt(r_int,2)} Ω</text>

  <rect class="srcBox" x="110" y="175" width="240" height="280" rx="28"/>
  <text class="textW label" x="230" y="235" text-anchor="middle" font-size="28">FONTE</text>

  <rect class="srcInner" x="145" y="265" width="170" height="78" rx="18"/>
  <text class="textW panelText2" x="230" y="315" text-anchor="middle" fill="#5eead4">ε = {fmt_voltage(epsilon)}</text>

  <!-- símbolo da bateria -->
  <line x1="195" y1="372" x2="275" y2="372" stroke="#e8eefc" stroke-width="7" stroke-linecap="round"/>
  <line x1="212" y1="406" x2="258" y2="406" stroke="#e8eefc" stroke-width="7" stroke-linecap="round"/>
  <text class="textW tiny" x="285" y="378">+</text>
  <text class="textW tiny" x="265" y="416">−</text>

  <!-- Nós da fonte -->
  <circle class="node" cx="350" cy="270" r="7"/>
  <circle class="node" cx="350" cy="430" r="7"/>

  <!-- Reostato (centro) -->
  <!-- Caixa do componente (não cobre o fio porque o fio será desenhado depois) -->
  <rect class="panelYellow" x="640" y="225" width="520" height="130" rx="18" filter="url(#panelGlowYellow)"/>

  <!-- Nós do reostato -->
  <circle class="node" cx="660" cy="270" r="7"/>
  <circle class="node" cx="1140" cy="270" r="7"/>

  <!-- Zigzag (símbolo) -->
  <path class="wireThin" d="
    M 660 270
    L 705 240
    L 750 300
    L 795 240
    L 840 300
    L 885 240
    L 930 300
    L 975 240
    L 1020 300
    L 1065 240
    L 1110 300
    L 1140 270
  " />

  <!-- seta do reostato -->
  <line x1="835" y1="220" x2="980" y2="350" stroke="#f7b500" stroke-width="7" stroke-linecap="round" filter="url(#panelGlowYellow)"/>
  <polygon points="975,350 1010,352 992,322" fill="#f7b500" filter="url(#panelGlowYellow)"/>

  <!-- Texto do reostato embaixo (como você pediu) -->
  <text class="textW label" x="900" y="410" text-anchor="middle">Reostato (série)</text>
  <text class="textW subLabel" x="900" y="445" text-anchor="middle">R = {fmt(R,2)} Ω</text>

  <!-- Voltímetro (acima, sem sobrepor o reostato) -->
  <text class="textW label" x="900" y="88" text-anchor="middle">Voltímetro (paralelo)</text>

  <circle class="meterCircle" cx="900" cy="135" r="44"/>
  <text class="textW meterSymbol" x="900" y="149" text-anchor="middle">V</text>

  <rect class="panelPurple" x="770" y="175" width="260" height="70" rx="16" filter="url(#panelGlowPurple)"/>
  <text class="textW panelText2" x="900" y="220" text-anchor="middle">V = {fmt_voltage(V)}</text>

  <!-- Amperímetro (direita) -->
  <circle class="meterCircle" cx="1370" cy="270" r="46"/>
  <text class="textW meterSymbol" x="1370" y="285" text-anchor="middle">A</text>

  <text class="textW label" x="1600" y="240" text-anchor="middle">Amperímetro (série)</text>
  <rect class="panelGreen" x="1470" y="260" width="340" height="82" rx="16" filter="url(#panelGlowGreen)"/>
  <text class="textW panelText2" x="1640" y="312" text-anchor="middle" fill="#86efac">I = {fmt_current(I)}</text>

  <!-- =======================
       Fios (por último)
       para NÃO ficarem escondidos
       ======================= -->

  <!-- Malha superior: fonte -> reostato -> amperímetro -> direita -->
  <path class="wire" d="M 350 270 L 660 270" />
  <path class="wire" d="M 1140 270 L 1324 270" />
  <path class="wire" d="M 1416 270 L 1820 270" />

  <!-- Lado direito descendo para o retorno -->
  <path class="wire" d="M 1820 270 L 1820 430" />

  <!-- Retorno inferior: direita -> fonte -->
  <path class="wire" d="M 1820 430 L 350 430" />

  <!-- Conexões da fonte até a malha (entrada/saída) -->
  <path class="wireThin" d="M 350 270 L 350 215" />
  <path class="wireThin" d="M 350 430 L 350 425" />

  <!-- Paralelo do voltímetro: liga nos terminais do reostato -->
  <path class="wireThin" d="M 660 270 L 660 135 L 856 135" />
  <path class="wireThin" d="M 1140 270 L 1140 135 L 944 135" />

  <!-- legenda -->
  <text class="textW tiny" x="70" y="510">
    Série: fonte → reostato → amperímetro. Paralelo: voltímetro (medindo a tensão nos terminais do reostato).
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
components.html(svg_html, height=580, scrolling=False)

st.divider()

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
