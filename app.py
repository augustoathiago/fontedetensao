import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

# ----------------------------
# Configuração da página
# ----------------------------
st.set_page_config(
    page_title="Simulador Fonte de Tensão Física II",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS: melhorar leitura no celular + containers com scroll lateral (touch)
st.markdown("""
<style>
/* Deixa a página mais "mobile-friendly" */
.block-container { padding-top: 1.0rem; padding-bottom: 2rem; }

/* Títulos um pouco mais compactos em telas pequenas */
@media (max-width: 600px) {
  h1 { font-size: 1.45rem !important; }
  h2 { font-size: 1.15rem !important; }
  h3 { font-size: 1.02rem !important; }
}

/* Container com scroll horizontal e suporte a "arrastar com o dedo" */
.hscroll {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border: 1px solid rgba(49,51,63,0.2);
  border-radius: 10px;
  padding: 10px;
  background: white;
}

/* Dica visual */
.hscroll-hint {
  font-size: 0.9rem;
  opacity: 0.75;
  margin: 0.1rem 0 0.6rem 0;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Helpers de formatação (pt-BR)
# ----------------------------
def fmt(x, nd=3):
    """Formata número com vírgula decimal (padrão BR) e sem notação estranha."""
    try:
        s = f"{x:.{nd}f}"
    except Exception:
        s = str(x)
    return s.replace(".", ",")

def fmt_int(x):
    try:
        return str(int(round(x)))
    except Exception:
        return str(x)

# ----------------------------
# Faixas realistas (você pode ajustar)
# Mantemos também valores "globais" para FIXAR escala dos eixos
# ----------------------------
EPS_MIN, EPS_MAX = 1.0, 24.0          # V (baterias/fonte de bancada baixa tensão)
RINT_MIN, RINT_MAX = 0.5, 10.0        # ohm (resistência interna didática)
RLOAD_MIN, RLOAD_MAX = 0.5, 200.0     # ohm (reostato/carga)

# Eixos fixos:
I_AXIS_MAX = EPS_MAX / RINT_MIN       # maior corrente de curto possível na faixa
V_AXIS_MAX = EPS_MAX
P_AXIS_MAX = (EPS_MAX**2) / (4*RINT_MIN)  # potência útil máxima teórica na faixa

# Margens “bonitinhas”
I_AXIS_MAX_PAD = float(np.ceil(I_AXIS_MAX / 5) * 5)   # arredonda para cima múltiplo de 5
V_AXIS_MAX_PAD = float(np.ceil(V_AXIS_MAX / 2) * 2)   # múltiplo de 2
P_AXIS_MAX_PAD = float(np.ceil(P_AXIS_MAX / 50) * 50) # múltiplo de 50

# ----------------------------
# Início: duas colunas (logo + título/descrição)
# ----------------------------
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

# ----------------------------
# Seção: Equação característica
# ----------------------------
st.header("Equação característica")
st.latex(r"V = \varepsilon - r\,I")
st.write(
    "**V** é a tensão no circuito (V), **ε** é a tensão na fonte (V) (ou força eletromotriz), "
    "**r** é a resistência interna da fonte (Ω) e **I** é a corrente no circuito (A)."
)

st.divider()

# ----------------------------
# Seção: Parâmetros (sliders)
# ----------------------------
st.header("Parâmetros")

# Em telas grandes, 3 colunas; no celular, o Streamlit empilha automaticamente
c1, c2, c3 = st.columns(3)

with c1:
    epsilon = st.slider(
        "ε (tensão na fonte) [V]",
        min_value=float(EPS_MIN),
        max_value=float(EPS_MAX),
        value=12.0,
        step=0.5,
        help="Faixa típica de fonte de bancada/baterias em laboratório didático."
    )

with c2:
    r_int = st.slider(
        "r (resistência interna) [Ω]",
        min_value=float(RINT_MIN),
        max_value=float(RINT_MAX),
        value=2.0,
        step=0.1,
        help="Em fontes reais r é pequeno, mas aqui usamos uma faixa didática para enxergar efeitos."
    )

with c3:
    R = st.slider(
        "R (resistência do circuito / reostato) [Ω]",
        min_value=float(RLOAD_MIN),
        max_value=float(RLOAD_MAX),
        value=20.0,
        step=0.5,
        help="Representa a carga externa (reostato) usada para variar a corrente no circuito."
    )

# ----------------------------
# Cálculos principais
# ----------------------------
I = epsilon / (r_int + R)                 # A
V = epsilon - r_int * I                   # V (equivale a I*R)
icc = epsilon / r_int                     # A
Pg = epsilon * I                          # W (potência geradora)
Pd = r_int * I**2                         # W (potência dissipada internamente)
P_util = V * I                            # W (potência útil na carga)
eta = (P_util / Pg) if Pg > 0 else 0.0    # rendimento

# Valores do ponto de máxima potência útil
I_opt = icc / 2.0
V_opt = epsilon / 2.0

# ----------------------------
# Seção: Circuito (SVG grande + scroll horizontal / arrastar)
# ----------------------------
st.header("Circuito")

st.markdown('<div class="hscroll-hint">💡 Dica: no celular, arraste a figura para os lados.</div>',
            unsafe_allow_html=True)

# SVG do circuito: fonte com r interno, reostato R, voltímetro e amperímetro
# (desenhado maior para garantir legibilidade; container permite scroll horizontal)
svg = f"""
<div class="hscroll">
<svg width="980" height="280" viewBox="0 0 980 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .w {{ stroke:#111; stroke-width:3; fill:none; }}
      .t {{ font-family: Arial, Helvetica, sans-serif; font-size:18px; fill:#111; }}
      .ts {{ font-family: Arial, Helvetica, sans-serif; font-size:16px; fill:#111; }}
      .box {{ fill:#fff; stroke:#111; stroke-width:2; }}
      .meter {{ fill:#fff; stroke:#111; stroke-width:2; }}
    </style>
  </defs>

  <!-- Fios retangulares do circuito -->
  <!-- superior -->
  <line class="w" x1="120" y1="60" x2="860" y2="60"/>
  <!-- inferior -->
  <line class="w" x1="120" y1="220" x2="860" y2="220"/>
  <!-- laterais -->
  <line class="w" x1="120" y1="60" x2="120" y2="220"/>
  <line class="w" x1="860" y1="60" x2="860" y2="220"/>

  <!-- Fonte + resistência interna no ramo esquerdo -->
  <!-- símbolo simplificado: bloco "Fonte" e bloco "r" em série -->
  <rect class="box" x="60" y="95" width="120" height="50" rx="10"/>
  <text class="t" x="120" y="125" text-anchor="middle">Fonte</text>
  <text class="ts" x="120" y="148" text-anchor="middle">ε = {fmt(epsilon,2)} V</text>

  <!-- Conexões da fonte ao fio -->
  <line class="w" x1="120" y1="60" x2="120" y2="95"/>
  <line class="w" x1="120" y1="145" x2="120" y2="220"/>

  <!-- Resistência interna r (bloco) em série na esquerda, entre fonte e circuito -->
  <rect class="box" x="200" y="110" width="90" height="30" rx="8"/>
  <text class="ts" x="245" y="132" text-anchor="middle">r = {fmt(r_int,2)} Ω</text>

  <!-- Ligações entre fonte e r -->
  <line class="w" x1="180" y1="125" x2="200" y2="125"/>
  <!-- Ligações entre r e circuito -->
  <line class="w" x1="290" y1="125" x2="320" y2="125"/>
  <line class="w" x1="320" y1="125" x2="320" y2="60"/>
  <line class="w" x1="320" y1="125" x2="320" y2="220"/>

  <!-- Reostato / carga no ramo direito (símbolo como bloco + seta) -->
  <rect class="box" x="650" y="100" width="160" height="60" rx="10"/>
  <text class="t" x="730" y="128" text-anchor="middle">Reostato</text>
  <text class="ts" x="730" y="152" text-anchor="middle">R = {fmt(R,2)} Ω</text>
  <!-- seta diagonal do reostato -->
  <line class="w" x1="670" y1="165" x2="800" y2="95"/>
  <polyline class="w" points="792,98 804,92 798,104"/>

  <!-- Conexões do reostato ao fio -->
  <line class="w" x1="650" y1="130" x2="860" y2="130"/>
  <line class="w" x1="650" y1="130" x2="650" y2="60"/>
  <line class="w" x1="650" y1="130" x2="650" y2="220"/>

  <!-- Amperímetro em série no ramo inferior (círculo com A) -->
  <circle class="meter" cx="470" cy="220" r="28"/>
  <text class="t" x="470" y="227" text-anchor="middle">A</text>
  <text class="ts" x="470" y="260" text-anchor="middle">I = {fmt(I,3)} A</text>

  <!-- Voltímetro em paralelo no circuito (círculo com V) -->
  <circle class="meter" cx="470" cy="60" r="28"/>
  <text class="t" x="470" y="67" text-anchor="middle">V</text>
  <text class="ts" x="470" y="25" text-anchor="middle">V = {fmt(V,3)} V</text>

  <!-- Rótulos de tensão do circuito -->
  <text class="ts" x="900" y="120" text-anchor="end">Tensão no circuito: V</text>

</svg>
</div>
"""
components.html(svg, height=330, scrolling=False)

st.divider()

# ----------------------------
# Seção: Gráfico (Curva característica da fonte)
# ----------------------------
st.header("Gráfico")
st.subheader("Curva característica da fonte")

# Reta V = epsilon - r I, de I=0 até I=icc
I_line = np.linspace(0, icc, 200)
V_line = epsilon - r_int * I_line

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=I_line, y=V_line,
    mode="lines",
    name="V = ε - r·I",
    line=dict(width=3)
))

# Ponto vermelho no estado atual (R escolhido)
fig1.add_trace(go.Scatter(
    x=[I], y=[V],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12),
    text=[f"  (I={fmt(I,3)} A, V={fmt(V,3)} V)"],
    textposition="middle right"
))

# Marca do curto-circuito
fig1.add_trace(go.Scatter(
    x=[icc], y=[0],
    mode="markers+text",
    name="Curto-circuito",
    marker=dict(color="#444", size=10),
    text=[f"  icc = {fmt(icc,3)} A"],
    textposition="top left"
))

fig1.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=420,
    xaxis=dict(title="Corrente no circuito I (A)", range=[0, I_AXIS_MAX_PAD], fixedrange=True),
    yaxis=dict(title="Tensão no circuito V (V)", range=[0, V_AXIS_MAX_PAD], fixedrange=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig1, width="stretch", theme="streamlit")

st.caption("a resistência do reostato do circuito foi alterada para obtermos diferentes valores de tensão e corrente do circuito")

# Texto com valores atuais
st.write(
    f"**Para o valor atual de R:**  I = **{fmt(I,3)} A** e V = **{fmt(V,3)} V**. "
    f"**Corrente de curto-circuito:** icc = **{fmt(icc,3)} A**."
)

st.divider()

# ----------------------------
# Seção: Potência
# ----------------------------
st.header("Potência")

st.write("**Potência = energia por tempo (unidade Watts)**")
st.write("**A partir da equação característica:**")
st.latex(r"V\,I = \varepsilon\,I - r\,I^2")
st.latex(r"P_{\mathrm{útil}} = P_g - P_d")

# Curva P_util(I) = epsilon*I - r*I^2, somente no intervalo [0, icc]
I_pow = np.linspace(0, icc, 250)
P_curve = epsilon * I_pow - r_int * I_pow**2

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=I_pow, y=P_curve,
    mode="lines",
    name="Pútil(I)",
    line=dict(width=3)
))

# Ponto vermelho no estado atual
fig2.add_trace(go.Scatter(
    x=[I], y=[P_util],
    mode="markers+text",
    name="Ponto de operação",
    marker=dict(color="red", size=12),
    text=[f"  Pútil={fmt(P_util,3)} W"],
    textposition="middle right"
))

# Ponto de máximo (I = icc/2)
P_max = epsilon * I_opt - r_int * I_opt**2
fig2.add_trace(go.Scatter(
    x=[I_opt], y=[P_max],
    mode="markers+text",
    name="Máximo",
    marker=dict(color="#222", size=10),
    text=[f"  Máx em I=icc/2"],
    textposition="top left"
))

fig2.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=420,
    xaxis=dict(title="Corrente I (A)", range=[0, I_AXIS_MAX_PAD], fixedrange=True),
    yaxis=dict(title="Potência útil Pútil (W)", range=[0, P_AXIS_MAX_PAD], fixedrange=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig2, width="stretch", theme="streamlit")

st.write(
    f"Para **Pútil máximo**, a corrente deve ser **icc/2 = {fmt(I_opt,3)} A**, "
    f"caso onde a tensão do circuito é **ε/2 = {fmt(V_opt,3)} V**."
)

st.divider()

# ----------------------------
# Seção: Rendimento
# ----------------------------
st.header("Rendimento")

st.latex(r"\eta = \dfrac{P_{\mathrm{útil}}}{P_g}")

st.write(
    f"Para o valor atual de **R = {fmt(R,2)} Ω**:"
)
st.write(
    f"- **Pútil = {fmt(P_util,3)} W**  (na carga)\n"
    f"- **Pg = {fmt(Pg,3)} W**  (gerada pela fonte)\n"
    f"- **Pd = {fmt(Pd,3)} W**  (dissipada na resistência interna)"
)

st.metric("Rendimento η", f"{fmt(100*eta,2)} %")
