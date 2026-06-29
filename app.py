import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# Simulador NK simple: OA–RPM
# Dinero, Crédito y Bancos · UNS
# Versión guiada para clase
# =========================================================

st.set_page_config(
    page_title="Simulador NK OA–RPM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Estética ----------
NAVY = "#1B2A4A"
NAVY_DARK = "#101A2F"
NAVY_CARD = "#223356"
SIDEBAR = "#F3F6FB"
SIDEBAR_TEXT = "#172542"
GOLD = "#C9A84C"
GOLD_LIGHT = "#E4C86A"
WHITE = "#FFFFFF"
MUTED = "#DDE6F6"
PINK = "#FF5B6E"
GREEN = "#31B57B"
BLUE = "#73B7FF"
RED = "#FF6B6B"
GRAY = "rgba(255,255,255,0.34)"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, {NAVY} 0%, {NAVY_DARK} 100%);
        color: {WHITE};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR};
        border-right: 2px solid rgba(201,168,76,0.55);
    }}
    section[data-testid="stSidebar"] * {{
        color: {SIDEBAR_TEXT} !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        color: {SIDEBAR_TEXT} !important;
        background-color: #FFFFFF;
        border: 1px solid rgba(27,42,74,0.25);
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {GOLD};
        border-color: {GOLD};
        color: #111A2E !important;
    }}
    h1, h2, h3 {{
        color: {WHITE};
        font-family: Georgia, 'Times New Roman', serif;
    }}
    h4, h5, h6, p, li, label, span {{ color: {WHITE}; }}
    .subtitle {{ color: {MUTED}; font-size: 1.06rem; }}
    .gold {{ color: {GOLD_LIGHT}; font-weight: 800; }}
    .card {{
        background-color: rgba(34, 51, 86, 0.98);
        border: 1px solid rgba(201,168,76,0.40);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.22);
        margin-bottom: 0.85rem;
    }}
    .result-card {{
        background-color: rgba(34, 51, 86, 0.98);
        border: 1px solid rgba(201,168,76,0.35);
        border-radius: 14px;
        padding: 0.75rem 0.85rem;
        min-height: 84px;
    }}
    .result-label {{
        color: {MUTED};
        font-size: 0.86rem;
        line-height: 1.15rem;
        margin-bottom: 0.25rem;
    }}
    .result-value {{
        color: {WHITE};
        font-size: 1.75rem;
        font-weight: 800;
    }}
    .small {{ color: {MUTED}; font-size: 0.92rem; }}
    .pill {{
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        background: rgba(201,168,76,0.18);
        color: {GOLD_LIGHT};
        border: 1px solid rgba(201,168,76,0.40);
        font-weight: 700;
        margin: 0.15rem 0.2rem 0.15rem 0;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(46, 59, 92, 0.75);
        border-radius: 999px;
        color: {WHITE};
        padding: 8px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {GOLD};
        color: #111A2E !important;
        font-weight: 700;
    }}
    .stButton > button {{
        background-color: rgba(46, 59, 92, 0.9);
        color: #FFFFFF !important;
        border: 1px solid rgba(201,168,76,0.45);
        border-radius: 999px;
    }}
    .stButton > button:hover {{
        background-color: {GOLD};
        color: #111A2E !important;
        border: 1px solid {GOLD};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Utilidades ----------
def safe_div(num, den, fallback=np.nan):
    if abs(den) < 1e-9:
        return fallback
    return num / den


def result_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">{label}</div>
            <div class="result-value">{value}</div>
            <div class="small">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Escenarios guiados ----------
DEFAULTS = {
    "pi_bar_0": 2.0,
    "pi_e_0": 2.0,
    "theta": 0.60,
    "lam": 1.00,
    "phi": 1.00,
    "a": 1.50,
    "b": 0.50,
    "r_star_base": 1.00,
}

SCENARIOS = {
    "Equilibrio inicial": {
        "desc": "Punto de referencia: expectativas en la meta y shocks nulos.",
        "mu": 0.0,
        "eps": 0.0,
        "delta_A": 0.0,
        "delta_ybar": 0.0,
        "pi_bar": 2.0,
        "pi_e": 2.0,
        "moves": "No se desplazan curvas. La economía parte en E₀.",
    },
    "Shock transitorio de demanda": {
        "desc": "Aumento temporario de la demanda agregada, representado por μ > 0.",
        "mu": 0.8,
        "eps": 0.0,
        "delta_A": 0.0,
        "delta_ybar": 0.0,
        "pi_bar": 2.0,
        "pi_e": 2.0,
        "moves": "Con Taylor se desplaza la RPM. Con RMO, la tasa neutraliza el shock.",
    },
    "Aumento permanente de G": {
        "desc": "Aumento permanente de A/G financiado con deuda: cambia la tasa real neutral, no μ.",
        "mu": 0.0,
        "eps": 0.0,
        "delta_A": 0.8,
        "delta_ybar": 0.0,
        "pi_bar": 2.0,
        "pi_e": 2.0,
        "moves": "En el plano π-y casi no se mueve nada: el efecto central es ↑ r̄ y crowding out.",
    },
    "Shock transitorio de OA": {
        "desc": "Shock inflacionario de costos, representado por ε > 0.",
        "mu": 0.0,
        "eps": 0.8,
        "delta_A": 0.0,
        "delta_ybar": 0.0,
        "pi_bar": 2.0,
        "pi_e": 2.0,
        "moves": "Se desplaza la OA hacia arriba/izquierda. Aparece estanflación.",
    },
    "Shock permanente de OA/productividad": {
        "desc": "Caída permanente del producto potencial, representada por Δȳ < 0.",
        "mu": 0.0,
        "eps": 0.0,
        "delta_A": 0.0,
        "delta_ybar": -0.8,
        "pi_bar": 2.0,
        "pi_e": 2.0,
        "moves": "Cambia la línea de producto potencial vigente. La referencia de pleno empleo se mueve.",
    },
    "Caída de expectativas de inflación": {
        "desc": "Las expectativas caen por debajo de la meta: πᵉ < π̄.",
        "mu": 0.0,
        "eps": 0.0,
        "delta_A": 0.0,
        "delta_ybar": 0.0,
        "pi_bar": 2.0,
        "pi_e": 1.2,
        "moves": "La OA se desplaza hacia abajo/derecha; la tasa real puede contraer la demanda.",
    },
    "Baja de la meta de inflación": {
        "desc": "La autoridad baja π̄, pero las expectativas todavía no se ajustaron plenamente.",
        "mu": 0.0,
        "eps": 0.0,
        "delta_A": 0.0,
        "delta_ybar": 0.0,
        "pi_bar": 1.2,
        "pi_e": 2.0,
        "moves": "La nueva meta queda por debajo de πᵉ: el costo depende de credibilidad y velocidad de ajuste.",
    },
}

# ---------- Header ----------
st.markdown(
    """
    # Simulador NK · OA–RPM
    <p class="subtitle">Laboratorio guiado para comparar <span class="gold">equilibrio inicial vs. shock</span> bajo <span class="gold">Regla de Taylor</span> y <span class="gold">Regla Monetaria Óptima</span>.</p>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 1) Elegí el caso")
    scenario_name = st.selectbox("Escenario", list(SCENARIOS.keys()), index=0)

    st.markdown("### 2) Elegí la regla")
    regla = st.radio("Regla de política monetaria", ["Taylor", "Regla Monetaria Óptima"], index=0)

    st.markdown("---")
    st.markdown("### Parámetros avanzados")
    st.caption("Para la primera lectura, no hace falta tocar esto. Sirve para ver pendientes y sensibilidad.")

    with st.expander("Mostrar sliders avanzados", expanded=False):
        theta = st.slider("θ · pendiente de OA", 0.20, 1.20, DEFAULTS["theta"], step=0.05)
        lam = st.slider("λ · peso del producto en RMO", 0.20, 3.00, DEFAULTS["lam"], step=0.05)
        phi = st.slider("φ · sensibilidad de DA a tasa real", 0.40, 2.00, DEFAULTS["phi"], step=0.05)
        a = st.slider("a · Taylor responde a inflación", 1.10, 2.40, DEFAULTS["a"], step=0.05)
        b = st.slider("b · Taylor responde a producto", 0.00, 1.20, DEFAULTS["b"], step=0.05)
        r_star_base = st.slider("r̄ · tasa real neutral inicial", 0.0, 3.0, DEFAULTS["r_star_base"], step=0.1)

        st.markdown("**Tamaño del shock seleccionado**")
        mu_override = st.slider("μ · DA transitorio", -1.20, 1.20, SCENARIOS[scenario_name]["mu"], step=0.1)
        eps_override = st.slider("ε · OA transitorio", -1.20, 1.20, SCENARIOS[scenario_name]["eps"], step=0.1)
        dA_override = st.slider("∆A · G/A permanente", -1.00, 1.20, SCENARIOS[scenario_name]["delta_A"], step=0.1)
        dybar_override = st.slider("∆ȳ · potencial permanente", -1.20, 1.00, SCENARIOS[scenario_name]["delta_ybar"], step=0.1)
    # Defaults when expander not touched: variables still set by the widgets above because Streamlit executes them.

scenario = SCENARIOS[scenario_name]

# Advanced widgets always set these variables. Use them as current shocks.
pi_bar_0 = DEFAULTS["pi_bar_0"]
pi_e_0 = DEFAULTS["pi_e_0"]
pi_bar = scenario["pi_bar"]
pi_e = scenario["pi_e"]
mu = mu_override
_eps = eps_override
delta_A = dA_override
delta_ybar = dybar_override

# ---------- Modelo ----------
# Eje horizontal: producto medido como desvío respecto del potencial inicial.
y_grid = np.linspace(-3, 3, 401)

def solve_model(pi_bar, pi_e, mu, eps, delta_A, delta_ybar, rule):
    gap_current_grid = y_grid - delta_ybar
    r_bar_current = r_star_base + safe_div(delta_A, phi, 0.0)
    neutral_nominal = r_bar_current + pi_bar

    oa = pi_e + theta * gap_current_grid + eps
    k_taylor = safe_div(1 + b * phi, (a - 1) * phi)
    tau_taylor = safe_div(mu, (a - 1) * phi)
    rpm_taylor = pi_bar - k_taylor * gap_current_grid + tau_taylor
    rpm_rmo = pi_bar - safe_div(lam, theta) * gap_current_grid

    gap_eq_taylor = safe_div(pi_bar - pi_e - eps + tau_taylor, theta + k_taylor)
    y_eq_taylor = gap_eq_taylor + delta_ybar
    pi_eq_taylor = pi_e + theta * gap_eq_taylor + eps
    i_taylor = r_bar_current + pi_bar + a * (pi_eq_taylor - pi_bar) + b * gap_eq_taylor

    gap_eq_rmo = safe_div(theta, theta**2 + lam) * (pi_bar - pi_e - eps)
    y_eq_rmo = gap_eq_rmo + delta_ybar
    pi_eq_rmo = pi_e + theta * gap_eq_rmo + eps
    c_rmo = safe_div(theta, phi * (theta**2 + lam))
    i_rmo = r_bar_current + pi_e + c_rmo * (pi_e - pi_bar + eps) + safe_div(mu, phi)

    if rule == "Taylor":
        return {
            "oa": oa,
            "rpm": rpm_taylor,
            "y_eq": y_eq_taylor,
            "gap_eq": gap_eq_taylor,
            "pi_eq": pi_eq_taylor,
            "i": i_taylor,
            "r_bar": r_bar_current,
            "i_gap": i_taylor - neutral_nominal,
            "rpm_label": "RPM final · Taylor",
        }
    return {
        "oa": oa,
        "rpm": rpm_rmo,
        "y_eq": y_eq_rmo,
        "gap_eq": gap_eq_rmo,
        "pi_eq": pi_eq_rmo,
        "i": i_rmo,
        "r_bar": r_bar_current,
        "i_gap": i_rmo - neutral_nominal,
        "rpm_label": "RPM final · RMO",
    }

initial = solve_model(pi_bar_0, pi_e_0, 0.0, 0.0, 0.0, 0.0, regla)
final = solve_model(pi_bar, pi_e, mu, _eps, delta_A, delta_ybar, regla)

gap_current_grid_final = y_grid - delta_ybar

# ---------- Layout ----------
intro_left, intro_right = st.columns([1.3, 1.0], gap="large")
with intro_left:
    st.markdown(
        f"""
        <div class="card">
        <span class="pill">{scenario_name}</span>
        <span class="pill">{regla}</span>
        <h3 style="margin-top:0.4rem;">Qué estás comparando</h3>
        <p>{scenario['desc']}</p>
        <p class="small"><b>Lectura visual:</b> {scenario['moves']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with intro_right:
    st.markdown(
        f"""
        <div class="card">
        <h3 style="margin-top:0;">Regla de uso</h3>
        <p>Primero mirá <b>E₀</b> y las curvas iniciales punteadas. Después mirá <b>E₁</b> y las curvas finales sólidas.</p>
        <p class="small">La escala queda fija para que se vea el desplazamiento de curvas, no un cambio de zoom.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

left, right = st.columns([1.55, 1.0], gap="large")

with left:
    st.markdown("### Gráfico OA–RPM")
    st.markdown(
        "<p class='small'>Eje horizontal: producto medido como desvío respecto del potencial inicial. Si cambia el potencial, aparece una nueva línea vertical punteada.</p>",
        unsafe_allow_html=True,
    )

    fig = go.Figure()

    # Curvas iniciales punteadas / suaves
    fig.add_trace(go.Scatter(
        x=y_grid, y=initial["oa"], mode="lines", name="OA inicial",
        line=dict(width=3, color="rgba(115,183,255,0.35)", dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=y_grid, y=initial["rpm"], mode="lines", name="RPM inicial",
        line=dict(width=3, color="rgba(228,200,106,0.38)", dash="dot")
    ))

    # Curvas finales sólidas
    fig.add_trace(go.Scatter(
        x=y_grid, y=final["oa"], mode="lines", name="OA final",
        line=dict(width=5, color=BLUE)
    ))
    fig.add_trace(go.Scatter(
        x=y_grid, y=final["rpm"], mode="lines", name=final["rpm_label"],
        line=dict(width=5, color=GOLD_LIGHT, dash="dash")
    ))

    # Equilibrios
    fig.add_trace(go.Scatter(
        x=[initial["y_eq"]], y=[initial["pi_eq"]], mode="markers+text", name="E₀ inicial",
        marker=dict(size=13, color=GOLD, line=dict(width=2, color="#111A2E")),
        text=["E₀"], textposition="bottom center"
    ))
    fig.add_trace(go.Scatter(
        x=[final["y_eq"]], y=[final["pi_eq"]], mode="markers+text", name="E₁ final",
        marker=dict(size=17, color=PINK, line=dict(width=2, color="#111A2E")),
        text=["E₁"], textposition="top center"
    ))

    # Referencias
    fig.add_vline(x=0, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.35)", annotation_text="ȳ₀", annotation_font_color="white")
    if abs(delta_ybar) > 0.01:
        fig.add_vline(x=delta_ybar, line_width=2, line_dash="dot", line_color="rgba(255,91,110,0.85)", annotation_text="ȳ₁", annotation_font_color="white")
    fig.add_hline(y=pi_bar_0, line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.30)", annotation_text="π̄₀", annotation_font_color="white")
    if abs(pi_bar - pi_bar_0) > 0.01:
        fig.add_hline(y=pi_bar, line_width=2, line_dash="dot", line_color="rgba(255,91,110,0.75)", annotation_text="π̄₁", annotation_font_color="white")

    fig.update_layout(
        height=620,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,26,47,0.98)",
        font=dict(color=WHITE, size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=20, t=45, b=60),
        xaxis=dict(
            title="Producto: y − ȳ₀",
            zeroline=False,
            gridcolor="rgba(255,255,255,0.13)",
            range=[-3, 3],
            dtick=1,
        ),
        yaxis=dict(
            title="Inflación π",
            zeroline=False,
            gridcolor="rgba(255,255,255,0.13)",
            range=[-1, 6],
            dtick=1,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### Resultados finales")
    st.markdown("<p class='small'>Estos valores corresponden al punto final E₁ bajo la regla elegida.</p>", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        result_card("Brecha del producto", f"{final['gap_eq']:.2f}", "y − ȳ vigente")
    with r1c2:
        result_card("Inflación", f"{final['pi_eq']:.2f}", "π")

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        result_card("Brecha inflacionaria", f"{final['pi_eq'] - pi_bar:.2f}", "π − π̄ vigente")
    with r2c2:
        result_card("Tasa nominal", f"{final['i']:.2f}", "i")

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        result_card("Cambio de tasa", f"{final['i_gap']:.2f}", "i − (r̄ + π̄)")
    with r3c2:
        result_card("Tasa real neutral", f"{final['r_bar']:.2f}", "r̄ vigente")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("#### Diagnóstico automático")
    bits = []
    if abs(delta_A) > 0.05:
        bits.append("Hay un **aumento permanente de G/A**: sube la tasa real neutral. En el gráfico π-y puede no verse movimiento, pero hay crowding out.")
    if abs(delta_ybar) > 0.05:
        if delta_ybar < 0:
            bits.append("Hay un **shock permanente negativo de oferta/productividad**: cae el producto potencial vigente, de ȳ₀ a ȳ₁.")
        else:
            bits.append("Hay un **shock permanente positivo de oferta/productividad**: sube el producto potencial vigente.")
    if mu > 0.05:
        bits.append("Hay un **shock transitorio positivo de demanda**. Con Taylor suele mover inflación y producto; con RMO puede neutralizarse vía tasa.")
    elif mu < -0.05:
        bits.append("Hay un **shock transitorio negativo de demanda**: tiende a contraer inflación y producto.")
    if _eps > 0.05:
        bits.append("Hay un **shock transitorio inflacionario de OA**: la OA final queda por encima de la inicial y aparece el dilema inflación–producto.")
    elif _eps < -0.05:
        bits.append("Hay un **shock transitorio desinflacionario de OA**: la OA final queda por debajo de la inicial.")
    if pi_e < pi_bar - 0.05:
        bits.append("Las expectativas están **por debajo de la meta**: baja la presión inflacionaria, pero puede subir la tasa real.")
    elif pi_e > pi_bar + 0.05:
        bits.append("Las expectativas están **por encima de la meta**: la autoridad necesita endurecer para reanclar.")
    if not bits:
        bits.append("La economía está en el equilibrio inicial: expectativas en la meta y shocks nulos.")

    if final["gap_eq"] < -0.10:
        bits.append("El producto final queda **por debajo del potencial vigente**.")
    elif final["gap_eq"] > 0.10:
        bits.append("El producto final queda **por encima del potencial vigente**.")
    else:
        bits.append("El producto final queda prácticamente en su potencial vigente.")

    if final["pi_eq"] > pi_bar + 0.10:
        bits.append("La inflación final queda **por encima de la meta vigente**.")
    elif final["pi_eq"] < pi_bar - 0.10:
        bits.append("La inflación final queda **por debajo de la meta vigente**.")
    else:
        bits.append("La inflación final queda prácticamente en la meta vigente.")

    for bit in bits:
        st.markdown(f"- {bit}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["Cómo usarlo", "Ecuaciones", "Comparar reglas", "Notas docentes"])

with tab1:
    st.markdown(
        """
        ### Secuencia sugerida para clase

        1. Elegí **Equilibrio inicial**. Identificá E₀, OA inicial y RPM inicial.
        2. Elegí **Shock transitorio de demanda** con **Taylor**. Mirá si se mueve la RPM y dónde queda E₁.
        3. Sin cambiar el shock, cambiá a **RMO**. Compará E₁ con el caso Taylor.
        4. Elegí **Shock transitorio de OA**. Mirá el desplazamiento de OA y el dilema: inflación sube, producto cae.
        5. Elegí **Aumento permanente de G**. El gráfico π-y puede casi no moverse: el resultado importante está en la tasa real neutral y en el crowding out.
        6. Recién después abrí **Parámetros avanzados** para ver cambios de pendiente: θ para OA, a/b para Taylor y λ para RMO.
        """
    )

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Modelo")
        st.latex(r"\pi = \pi^e + \theta (y-\bar y) + \varepsilon")
        st.markdown("### Regla de Taylor")
        st.latex(r"i=\bar r+\bar\pi+a(\pi-\bar\pi)+b(y-\bar y)")
        st.markdown("RPM derivada de Taylor:")
        st.latex(r"\pi-\bar\pi = -\frac{1+b\phi}{(a-1)\phi}(y-\bar y)+\frac{\mu}{(a-1)\phi}")
        st.markdown("<p class='small'>Importante: \(\bar r\) es tasa real neutral. La tasa nominal neutral es \(\bar r+\bar\pi\).</p>", unsafe_allow_html=True)
    with c2:
        st.markdown("### Regla Monetaria Óptima")
        st.latex(r"\pi-\bar\pi = -\frac{\lambda}{\theta}(y-\bar y)")
        st.latex(r"y-\bar y = \frac{\theta}{\theta^2+\lambda}(\bar\pi-\pi^e-\varepsilon)")
        st.markdown("Tasa nominal bajo RMO:")
        st.latex(r"i=\bar r+\pi^e+\frac{\theta}{\phi(\theta^2+\lambda)}(\pi^e-\bar\pi+\varepsilon)+\frac{1}{\phi}\mu")

with tab3:
    st.markdown("### Comparación numérica con el mismo shock")
    taylor = solve_model(pi_bar, pi_e, mu, _eps, delta_A, delta_ybar, "Taylor")
    rmo = solve_model(pi_bar, pi_e, mu, _eps, delta_A, delta_ybar, "Regla Monetaria Óptima")
    df = pd.DataFrame(
        {
            "Regla": ["Taylor", "RMO"],
            "Brecha producto y−ȳ": [taylor["gap_eq"], rmo["gap_eq"]],
            "Inflación π": [taylor["pi_eq"], rmo["pi_eq"]],
            "Brecha inflación π−π̄": [taylor["pi_eq"] - pi_bar, rmo["pi_eq"] - pi_bar],
            "Tasa nominal i": [taylor["i"], rmo["i"]],
            "Cambio de tasa i−(r̄+π̄)": [taylor["i_gap"], rmo["i_gap"]],
            "r̄ vigente": [taylor["r_bar"], rmo["r_bar"]],
        }
    )
    st.dataframe(df.round(3), use_container_width=True, hide_index=True)

with tab4:
    st.markdown(
        """
        ### Qué conviene enfatizar

        - Las curvas punteadas son el **equilibrio inicial**. Las curvas sólidas son el **escenario con shock**.
        - En un shock transitorio de demanda, la diferencia Taylor/RMO es central: Taylor reacciona a inflación y producto observados; RMO usa el shock para ajustar la tasa.
        - En un shock de oferta, el dilema aparece porque subir la tasa baja inflación pero también profundiza la caída del producto.
        - En un aumento permanente de G, puede parecer que “no pasa nada” en el gráfico. Eso está bien: lo que cambia es la tasa real neutral y la composición de la demanda.
        - Los sliders son para una segunda vuelta. Primero conviene usar solo casos discretos.
        """
    )

st.markdown(
    """
    <p class="small">Modelo didáctico de estática comparativa. Las magnitudes son ilustrativas y sirven para visualizar direcciones de cambio.</p>
    """,
    unsafe_allow_html=True,
)
