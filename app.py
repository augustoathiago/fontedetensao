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
  touch-action: pan-y; /* mantém scroll vertical da página; horizontal será via drag */
}

/* Garante que o SVG mantenha sua largura natural para permitir scroll */
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
# Circuito (NOVO SVG) + drag-to-scroll
# ============================
st.header("Circuito")
st.markdown('<div class="hscroll-hint">💡 Dica: no celular, arraste a figura para os lados.</div>', unsafe_allow_html=True)

# Desenho em SVG:
# - Fonte à esquerda com ε e r
# - Reostato em série à direita, com R em 2 casas decimais
# - Voltímetro em paralelo acima do reostato exibindo V
# - Amperímetro em série após o reostato exibindo I
#
# IMPORTANTE: é f-string -> chaves literais do CSS/JS precisam ser {{ e }}
svg_html = f"""
<div id="circuit-scroll" class="hscroll grabbable">
<svg width="1800" height="520" viewBox="0 0 1800 520" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Circuito elétrico com fonte, reostato, voltímetro e amperímetro">
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
      .label {{ font-size:28px; font-weight:700; }}
      .subLabel {{ font-size:22px; opacity:0.92; }}
      .panelText {{ font-size:26px; font-weight:700; }}
      .panelText2 {{ font-size:22px; font-weight:650; }}
      .panel {{
        fill: rgba(10,16,30,0.55);
        stroke: rgba(255,255,255,0.18);
        stroke-width: 2;
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
      .panelYellow {{
        fill: rgba(10,16,30,0.45);
        stroke:#f7b500;
        stroke-width:4;
      }}
      .meterCircle {{
        fill: rgba(10,16,30,0.65);
        stroke: rgba(255,255,255,0.20);
        stroke-width: 3;
      }}
      .meterSymbol {{ font-size:30px; font-weight:800; }}
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
      .tiny {{ font-size:18px; opacity:0.9; }}
    </style>
  </defs>

  <!-- fundo -->
  <rect class="bg" x="0" y="0" width="1800" height="520" rx="18"/>

  <!-- ============================
       Coordenadas principais
       ============================
       Fonte:       x ~ 90..320
       Nó topo:     y = 260
       Nó baixo:    y = 420
       Reostato:    x = 640..1080
       Amperímetro: x ~ 1280
       Barramento direito: x ~ 1680
  -->

  <!-- ======= Fonte (esquerda) ======= -->
  <text class="textW label" x="90" y="70">Fonte (ajustada em “Parâmetros”)</text>
  <text class="textW subLabel" x="90" y="105">ε = {fmt(epsilon,2)} V</text>
  <text class="textW subLabel" x="90" y="135">r = {fmt(r_int,2)} Ω</text>

  <!-- caixa da fonte -->
  <rect class="srcBox" x="110" y="170" width="210" height="250" rx="28"/>
  <text class="textW panelText" x="215" y="215" text-anchor="middle">FONTE</text>

  <!-- "display" interno -->
  <rect class="srcInner" x="140" y="235" width="150" height="70" rx="18"/>
  <text class="textW panelText2" x="215" y="279" text-anchor="middle" fill="#5eead4">ε = {fmt_voltage(epsilon)}</text>

  <!-- símbolo (bateria) dentro -->
  <!-- placa longa (positivo) e placa curta (negativo) -->
  <line x1="185" y1="330" x2="245" y2="330" stroke="#e8eefc" stroke-width="6" stroke-linecap="round"/>
  <line x1="198" y1="360" x2="232" y2="360" stroke="#e8eefc" stroke-width="6" stroke-linecap="round"/>
  <text class="textW tiny" x="255" y="336">+</text>
  <text class="textW tiny" x="240" y="372">−</text>

  <!-- terminais da fonte (nós) -->
  <circle class="node" cx="320" cy="260" r="7"/>
  <circle class="node" cx="320" cy="420" r="7"/>

  <!-- conexão da caixa aos nós -->
  <path class="wireThin" d="M 320 260 L 320 220" />
  <path class="wireThin" d="M 320 420 L 320 390" />

  <!-- ======= Barramento do circuito (retorno) ======= -->
  <!-- Fio superior: da fonte até reostato -->
  <path class="wire" d="M 320 260 L 640 260" />
  <!-- Fio inferior: retorno da direita até fonte -->
  <path class="wire" d="M 1680 420 L 320 420" />
  <!-- Lado direito fechando malha -->
  <path class="wire" d="M 1680 260 L 1680 420" />
  <!-- Subida da fonte (fechando malha à esquerda) -->
  <path class="wire" d="M 320 260 L 320 420" opacity="0.0" /> <!-- invisível: nós já indicam -->

  <!-- ======= Reostato (em série) ======= -->
  <text class="textW label" x="860" y="70" text-anchor="middle">Reostato (série)</text>
  <text class="textW subLabel" x="860" y="105" text-anchor="middle">R = {fmt(R,2)} Ω</text>

  <!-- nós do reostato -->
  <circle class="node" cx="640" cy="260" r="7"/>
  <circle class="node" cx="1080" cy="260" r="7"/>

  <!-- corpo do reostato: zigzag -->
  <path class="wireThin" d="
    M 640 260
    L 680 235
    L 720 285
    L 760 235
    L 800 285
    L 840 235
    L 880 285
    L 920 235
    L 960 285
    L 1000 235
    L 1040 285
    L 1080 260
  " />

  <!-- caixa sutil destacando o componente -->
  <rect class="panelYellow" x="620" y="200" width="480" height="120" rx="18" filter="url(#panelGlowYellow)"/>
  <text class="textW panelText2" x="860" y="328" text-anchor="middle" fill="#ffd36a">R = {fmt(R,2)} Ω</text>

  <!-- seta do reostato (cursor deslizante) -->
  <line x1="780" y1="195" x2="920" y2="315" stroke="#f7b500" stroke-width="6" stroke-linecap="round" filter="url(#panelGlowYellow)"/>
  <polygon points="915,315 945,320 930,292" fill="#f7b500" filter="url(#panelGlowYellow)"/>

  <!-- fio superior: continuação após reostato até amperímetro -->
  <path class="wire" d="M 1080 260 L 1238 260" />

  <!-- ======= Voltímetro (em paralelo ao reostato) ======= -->
  <text class="textW label" x="860" y="150" text-anchor="middle">Voltímetro (paralelo)</text>

  <!-- fios do paralelo (do nó esquerdo e direito do reostato até o voltímetro) -->
  <path class="wireThin" d="M 640 260 L 640 170 L 800 170" />
  <path class="wireThin" d="M 1080 260 L 1080 170 L 920 170" />

  <!-- voltímetro: círculo + painel -->
  <circle class="meterCircle" cx="860" cy="170" r="42" />
  <text class="textW meterSymbol" x="860" y="182" text-anchor="middle">V</text>

  <rect class="panelPurple" x="740" y="220" width="240" height="70" rx="16" filter="url(#panelGlowPurple)"/>
  <text class="textW panelText2" x="860" y="264" text-anchor="middle">
    V = {fmt_voltage(V)}
  </text>

  <!-- ======= Amperímetro (em série após o reostato) ======= -->
  <circle class="meterCircle" cx="1280" cy="260" r="44" />
  <text class="textW meterSymbol" x="1280" y="274" text-anchor="middle">A</text>

  <!-- fio superior: do amperímetro até direita -->
  <path class="wire" d="M 1324 260 L 1680 260" />

  <text class="textW label" x="1480" y="150" text-anchor="middle">Amperímetro (série)</text>
  <rect class="panelGreen" x="1380" y="180" width="320" height="80" rx="16" filter="url(#panelGlowGreen)"/>
  <text class="textW panelText2" x="1540" y="230" text-anchor="middle" fill="#86efac">
    I = {fmt_current(I)}
  </text>

  <!-- ======= Marcações do retorno inferior ======= -->
  <!-- conectores para dar sensação de malha completa -->
  <path class="wire" d="M 320 420 L 320 420" />
  <path class="wire" d="M 320 420 L 320 420" />

  <!-- fio da esquerda (caixa até nó inferior) já foi indicado; reforço visual -->
  <path class="wireThin" d="M 320 420 L 320 420" />

  <!-- legenda curta -->
  <text class="textW tiny" x="90" y="485" opacity="0.9">
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
    // impede a página de "brigar" com o gesto enquanto arrasta
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
components.html(svg_html, height=560, scrolling=False)

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
# Rendimento (CORRIGIDO)
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
