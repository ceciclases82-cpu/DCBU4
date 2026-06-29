import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# Simulador NK simple: OA–RPM
# Dinero, Crédito y Bancos · UNS
# =========================================================

st.set_page_config(
    page_title="Simulador NK OA–RPM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Estética ----------
NAVY = "#1B2A4A"
NAVY_2 = "#142039"
GOLD = "#C9A84C"
CARD = "#2E3B5C"
TEXT = "#FFFFFF"
MUTED = "#D8DEEA"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, {NAVY} 0%, {NAVY_2} 100%);
        color: {TEXT};
    }}
    section[data-testid="stSidebar"] {{
        background-color: #111A2E;
        border-right: 1px solid rgba(201,168,76,0.35);
    }}
    h1, h2, h3 {{
        color: {TEXT};
        font-family: Georgia, 'Times New Roman', serif;
    }}
    .gold {{ color: {GOLD}; font-weight: 700; }}
    .subtitle {{ color: {MUTED}; font-size: 1.05rem; }}
    .card {{
        background-color: rgba(46, 59, 92, 0.92);
        border: 1px solid rgba(201,168,76,0.35);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18);
        margin-bottom: 0.75rem;
    }}
    .small {{ color: {MUTED}; font-size: 0.92rem; }}
    div[data-testid="stMetric"] {{
        background-color: rgba(46, 59, 92, 0.88);
        border: 1px solid rgba(201,168,76,0.25);
        border-radius: 14px;
        padding: 0.8rem;
    }}
    div[data-testid="stMetricLabel"] {{ color: {MUTED}; }}
    div[data-testid="stMetricValue"] {{ color: {TEXT}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(46, 59, 92, 0.75);
        border-radius: 999px;
        color: {TEXT};
        padding: 8px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {GOLD};
        color: #111A2E;
        font-weight: 700;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def reset_params():
    st.session_state.pi_bar = 2.0
    st.session_state.pi_e = 2.0
    st.session_state.theta = 0.50
    st.session_state.lam = 1.00
    st.session_state.phi = 1.00
    st.session_state.a = 1.50
    st.session_state.b = 0.50
    st.session_state.mu = 0.00
    st.session_state.eps = 0.00


def preset_demand():
    reset_params()
    st.session_state.mu = 1.00


def preset_supply():
    reset_params()
    st.session_state.eps = 1.00


def preset_expectations():
    reset_params()
    st.session_state.pi_e = 1.00


def preset_target():
    reset_params()
    st.session_state.pi_bar = 1.00
    st.session_state.pi_e = 2.00


def safe_div(num, den, fallback=np.nan):
    if abs(den) < 1e-9:
        return fallback
    return num / den


for key, default in {
    "pi_bar": 2.0,
    "pi_e": 2.0,
    "theta": 0.50,
    "lam": 1.00,
    "phi": 1.00,
    "a": 1.50,
    "b": 0.50,
    "mu": 0.00,
    "eps": 0.00,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Header ----------
st.markdown(
    """
    # Simulador NK · OA–RPM
    <p class="subtitle">Laboratorio visual para comparar <span class="gold">Regla de Taylor</span> y <span class="gold">Regla Monetaria Óptima</span> ante shocks macroeconómicos.</p>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Escenario")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Equilibrio", on_click=reset_params, use_container_width=True)
        st.button("Shock DA", on_click=preset_demand, use_container_width=True)
    with c2:
        st.button("Shock OA", on_click=preset_supply, use_container_width=True)
        st.button("Caída πᵉ", on_click=preset_expectations, use_container_width=True)
    st.button("Baja de meta", on_click=preset_target, use_container_width=True)

    st.divider()
    regla = st.radio(
        "Regla de política monetaria",
        ["Taylor", "Regla Monetaria Óptima"],
        index=0,
    )

    st.divider()
    st.markdown("### Parámetros")
    st.slider("Meta de inflación π̄", -2.0, 8.0, key="pi_bar", step=0.1)
    st.slider("Inflación esperada πᵉ", -2.0, 8.0, key="pi_e", step=0.1)
    st.slider("θ · pendiente de OA", 0.05, 2.0, key="theta", step=0.05)
    st.slider("λ · peso del producto en RMO", 0.05, 5.0, key="lam", step=0.05)
    st.slider("φ · sensibilidad de DA a la tasa real", 0.10, 5.0, key="phi", step=0.10)

    st.markdown("### Taylor")
    st.slider("a · respuesta a inflación", 1.05, 4.0, key="a", step=0.05)
    st.slider("b · respuesta a brecha del producto", 0.0, 3.0, key="b", step=0.05)

    st.markdown("### Shocks")
    st.slider("μ · shock de demanda", -3.0, 3.0, key="mu", step=0.1)
    st.slider("ε · shock inflacionario / oferta", -3.0, 3.0, key="eps", step=0.1)

pi_bar = st.session_state.pi_bar
pi_e = st.session_state.pi_e
theta = st.session_state.theta
lam = st.session_state.lam
phi = st.session_state.phi
a = st.session_state.a
b = st.session_state.b
mu = st.session_state.mu
eps = st.session_state.eps

# ---------- Modelo ----------
x_grid = np.linspace(-6, 6, 301)
oa = pi_e + theta * x_grid + eps

# Taylor-derived RPM
k_taylor = safe_div(1 + b * phi, (a - 1) * phi)
tau_taylor = safe_div(mu, (a - 1) * phi)
rpm_taylor = pi_bar - k_taylor * x_grid + tau_taylor
x_taylor = safe_div(pi_bar - pi_e - eps + tau_taylor, theta + k_taylor)
pi_taylor = pi_e + theta * x_taylor + eps
i_gap_taylor = a * (pi_taylor - pi_bar) + b * x_taylor

# RMO
rpm_rmo = pi_bar - safe_div(lam, theta) * x_grid
x_rmo = safe_div(theta, theta**2 + lam) * (pi_bar - pi_e - eps)
pi_rmo = pi_e + theta * x_rmo + eps
i_gap_rmo = (
    (1 + safe_div(theta, phi * (theta**2 + lam))) * (pi_e - pi_bar)
    + safe_div(theta, phi * (theta**2 + lam)) * eps
    + safe_div(1, phi) * mu
)

if regla == "Taylor":
    rpm = rpm_taylor
    x_eq = x_taylor
    pi_eq = pi_taylor
    i_gap = i_gap_taylor
    rule_label = "RPM derivada de Taylor"
    rule_color = GOLD
else:
    rpm = rpm_rmo
    x_eq = x_rmo
    pi_eq = pi_rmo
    i_gap = i_gap_rmo
    rule_label = "RPM derivada de RMO"
    rule_color = GOLD

# ---------- Layout ----------
left, right = st.columns([1.35, 1.0], gap="large")

with left:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_grid,
            y=oa,
            mode="lines",
            name="OA",
            line=dict(width=4, color="#FFFFFF"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_grid,
            y=rpm,
            mode="lines",
            name=rule_label,
            line=dict(width=4, color=rule_color, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_eq],
            y=[pi_eq],
            mode="markers+text",
            name="Equilibrio",
            marker=dict(size=15, color="#F4D06F", line=dict(width=2, color="#111A2E")),
            text=["E"],
            textposition="top center",
        )
    )
    fig.add_vline(x=0, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.45)")
    fig.add_hline(y=pi_bar, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.45)")
    fig.update_layout(
        height=610,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,32,57,0.95)",
        font=dict(color=TEXT, size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=55, r=20, t=50, b=55),
        xaxis=dict(
            title="Brecha del producto x = y − ȳ",
            zeroline=False,
            gridcolor="rgba(255,255,255,0.12)",
            range=[-6, 6],
        ),
        yaxis=dict(
            title="Inflación π",
            zeroline=False,
            gridcolor="rgba(255,255,255,0.12)",
            range=[min(-2, np.nanmin([oa.min(), rpm.min(), pi_eq])-0.5), max(8, np.nanmax([oa.max(), rpm.max(), pi_eq])+0.5)],
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### Resultados")
    m1, m2, m3 = st.columns(3)
    m1.metric("x = y − ȳ", f"{x_eq:.2f}")
    m2.metric("π", f"{pi_eq:.2f}")
    m3.metric("i − ī", f"{i_gap:.2f}")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("#### Lectura rápida")
    if regla == "Taylor":
        st.markdown(
            r"""
            Con **Taylor**, la autoridad reacciona a la inflación y a la brecha del producto ya observadas.
            El shock de demanda `μ` entra en la RPM como ordenada al origen:

            $$\pi-\bar\pi=-\frac{1+b\phi}{(a-1)\phi}x+\frac{\mu}{(a-1)\phi}$$

            La tasa se calcula como:

            $$i-\bar i = a(\pi-\bar\pi)+bx$$
            """
        )
    else:
        st.markdown(
            r"""
            Con **RMO**, la autoridad usa información sobre shocks y elige la brecha óptima del producto.
            La RPM óptima es:

            $$\pi-\bar\pi=-\frac{\lambda}{\theta}x$$

            y la brecha queda:

            $$x=\frac{\theta}{\theta^2+\lambda}(\bar\pi-\pi^e-\varepsilon)$$

            La tasa incorpora directamente `μ`, `ε` y las expectativas.
            """
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("#### Diagnóstico automático")
    bits = []
    if mu > 0.05:
        bits.append("Hay un **shock positivo de demanda**: tiende a empujar producto e inflación hacia arriba.")
    elif mu < -0.05:
        bits.append("Hay un **shock negativo de demanda**: tiende a contraer producto e inflación.")

    if eps > 0.05:
        bits.append("Hay un **shock inflacionario de oferta**: la OA se desplaza hacia arriba y aparece el dilema inflación–producto.")
    elif eps < -0.05:
        bits.append("Hay un **shock desinflacionario de oferta**: la OA se desplaza hacia abajo.")

    if pi_e < pi_bar - 0.05:
        bits.append("Las expectativas están **por debajo de la meta**: baja la inflación esperada, pero puede haber canal contractivo por tasa real.")
    elif pi_e > pi_bar + 0.05:
        bits.append("Las expectativas están **por encima de la meta**: la autoridad necesita endurecer la política para reanclar inflación.")

    if not bits:
        bits.append("La economía está cerca del equilibrio inicial: expectativas en la meta y shocks nulos.")

    if x_eq < -0.10:
        bits.append("El resultado muestra **brecha negativa del producto**.")
    elif x_eq > 0.10:
        bits.append("El resultado muestra **brecha positiva del producto**.")
    else:
        bits.append("El producto queda prácticamente en su nivel potencial.")

    if pi_eq > pi_bar + 0.10:
        bits.append("La inflación queda **por encima de la meta**.")
    elif pi_eq < pi_bar - 0.10:
        bits.append("La inflación queda **por debajo de la meta**.")
    else:
        bits.append("La inflación queda prácticamente en la meta.")

    for bit in bits:
        st.markdown(f"- {bit}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Ecuaciones", "Guía para clase", "Comparar reglas"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Modelo")
        st.latex(r"x = y - \bar y")
        st.latex(r"\pi = \pi^e + \theta x + \varepsilon")
        st.markdown("### Taylor")
        st.latex(r"\pi-\bar\pi = -\frac{1+b\phi}{(a-1)\phi}x + \frac{\mu}{(a-1)\phi}")
        st.latex(r"i-\bar i = a(\pi-\bar\pi)+bx")
    with c2:
        st.markdown("### Regla Monetaria Óptima")
        st.latex(r"\pi-\bar\pi = -\frac{\lambda}{\theta}x")
        st.latex(r"x = \frac{\theta}{\theta^2+\lambda}(\bar\pi-\pi^e-\varepsilon)")
        st.latex(r"i-\bar i = \left(1+\frac{\theta}{\phi(\theta^2+\lambda)}\right)(\pi^e-\bar\pi)+\frac{\theta}{\phi(\theta^2+\lambda)}\varepsilon+\frac{1}{\phi}\mu")

with tab2:
    st.markdown(
        """
        ### Cómo usarlo en clase

        1. Arrancá en **Equilibrio**: πᵉ = π̄, μ = 0, ε = 0.
        2. Probá **Shock DA** y compará Taylor vs. RMO.
        3. Probá **Shock OA**: mostrar que ε > 0 empuja inflación, pero la respuesta contractiva genera brecha negativa.
        4. Probá **Caída πᵉ**: mostrar que el efecto sobre producto puede ser ambiguo según parámetros.
        5. Probá **Baja de meta**: mostrar el rol de credibilidad cuando πᵉ no baja junto con π̄.

        La frase clave: **la RPM es la relación que vemos en el gráfico; Taylor o RMO son las reglas que la justifican.**
        """
    )

with tab3:
    st.markdown("### Comparación numérica con los mismos parámetros")
    df = pd.DataFrame(
        {
            "Regla": ["Taylor", "RMO"],
            "x = y − ȳ": [x_taylor, x_rmo],
            "π": [pi_taylor, pi_rmo],
            "π − π̄": [pi_taylor - pi_bar, pi_rmo - pi_bar],
            "i − ī": [i_gap_taylor, i_gap_rmo],
        }
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown(
    """
    <p class="small">Modelo didáctico de estática comparativa. Las magnitudes son ilustrativas y dependen de la calibración elegida.</p>
    """,
    unsafe_allow_html=True,
)
