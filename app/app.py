"""
Mapa interactivo de la estructura económica provincial de Argentina (2004-2024).

Concurso Nacional de Visualización de Datos 2026 — "Contar con Datos"
Categoría: Exploración interactiva

Diseño: mapa a pantalla completa con tarjetas flotantes (HUD) encima.
Fuente de datos: CEPAL/MECON, "Desagregación provincial del VAB de la
Argentina, base 2004" (2022). Ver docs/diccionario_variables.md.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from casos_destacados import CASOS_DESTACADOS
from data_loader import (
    load_crecimiento_provincial,
    load_diversificacion_hhi,
    load_estructura_macrosectorial,
    load_geojson,
    load_vab_total,
)

st.set_page_config(
    page_title="Contar con Datos — Estructura económica provincial",
    layout="wide",
    initial_sidebar_state="collapsed",
)

FONT_FAMILY = "'Inter', 'Helvetica Neue', sans-serif"
TEXT_COLOR = "#1f2937"

MAPBOX_STYLE = "carto-positron-nolabels"
MAP_CENTER = {"lat": -40.0, "lon": -64.0}
MAP_ZOOM = 3.4

VISTA_CRECIMIENTO = "📈 Crecimiento"
VISTA_HHI = "🧩 Concentración sectorial"

# ---------------------------------------------------------------------------
# CSS: mapa ocupa toda la página, tarjetas flotantes encima
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: {FONT_FAMILY};
    }}

    /* Fondo del mismo color que el mar del basemap Carto Positron:
       cualquier franja no cubierta por el mapa queda invisible */
    .stApp, [data-testid="stMain"] {{
        background-color: #d4dadc !important;
    }}

    /* Ocultar el header de Streamlit y quitar todo el padding de la página */
    header[data-testid="stHeader"] {{
        display: none;
    }}
    [data-testid="stMainBlockContainer"] {{
        padding: 0 !important;
        max-width: 100% !important;
    }}
    [data-testid="stMain"] {{
        overflow: hidden;
    }}
    [data-testid="stVerticalBlock"] {{
        gap: 0.5rem;
    }}

    /* Tarjetas flotantes (HUD) */
    .st-key-hud_left, .st-key-hud_right {{
        position: fixed;
        top: 1rem;
        z-index: 999;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.14);
    }}
    .st-key-hud_left {{
        left: 1rem;
        width: 520px;
        max-height: calc(100vh - 2rem);
        overflow-y: auto;
    }}
    .st-key-hud_right {{
        right: 1rem;
        width: 400px;
        max-height: calc(100vh - 2rem);
        overflow-y: auto;
    }}

    /* Texto siempre oscuro dentro de las tarjetas, sin importar el tema */
    .st-key-hud_left *, .st-key-hud_right * {{
        color: {TEXT_COLOR} !important;
    }}
    .st-key-hud_left [data-testid="stMetricValue"],
    .st-key-hud_right [data-testid="stMetricValue"] {{
        color: #111827 !important;
        font-size: 1.35rem !important;
    }}
    .st-key-hud_left h3, .st-key-hud_right h3 {{
        font-size: 1.15rem !important;
        margin: 0 0 0.2rem 0 !important;
        padding: 0 !important;
    }}

    /* Botones del selector de vista totalmente redondeados */
    [data-testid="stButtonGroup"] button,
    button[data-testid="stBaseButton-segmented_control"],
    button[data-testid="stBaseButton-segmented_controlActive"] {{
        border-radius: 999px !important;
        margin-right: 0.35rem !important;
    }}

    /* Bordes redondeados en el fondo de la barra de color de Plotly */
    [data-testid="stPlotlyChart"] svg .cbbg {{
        rx: 10px;
        ry: 10px;
        stroke: none;
    }}

    /* Mapa fijo ocupando todo el viewport, sin franjas blancas */
    .st-key-map_full {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Altura real del viewport del navegador: se usa como altura exacta (en px)
# de la figura del mapa. OJO: el script corre dentro de un iframe de altura 0,
# por eso hay que consultar window.PARENT.innerHeight (la ventana real).
# En el primer render devuelve None (fallback 900) y el componente fuerza un
# rerun con el valor real.
viewport_height = streamlit_js_eval(js_expressions="window.parent.innerHeight", key="viewport_h")
MAP_HEIGHT = int(viewport_height) if viewport_height else 900

geojson = load_geojson()
vab_total = load_vab_total()
estructura = load_estructura_macrosectorial()
hhi = load_diversificacion_hhi()
crecimiento = load_crecimiento_provincial()

ANIO_MIN = int(vab_total["anio"].min())
ANIO_MAX = int(vab_total["anio"].max())


# ---------------------------------------------------------------------------
# Figuras cacheadas
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def build_growth_map(_geojson, df, height):
    fig = px.choropleth_map(
        df,
        geojson=_geojson,
        locations="provincia",
        featureidkey="properties.provincia",
        color="crecimiento_acumulado_pct",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        opacity=0.85,
        map_style=MAPBOX_STYLE,
        center=MAP_CENTER,
        zoom=MAP_ZOOM,
        hover_name="provincia",
        hover_data={
            "provincia": False,
            "crecimiento_acumulado_pct": ":.1f",
            "crecimiento_anual_promedio_pct": ":.1f",
        },
        labels={
            "crecimiento_acumulado_pct": "Crecimiento acumulado (%)",
            "crecimiento_anual_promedio_pct": "Crecimiento anual promedio (%)",
        },
    )
    fig.update_traces(marker_line_width=0.6, marker_line_color="white")
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        font=dict(family=FONT_FAMILY, size=13, color=TEXT_COLOR),
        coloraxis_colorbar=dict(
            title=dict(text="Crecimiento acumulado (%)", side="top", font=dict(color=TEXT_COLOR, size=12)),
            tickfont=dict(color=TEXT_COLOR, size=11),
            orientation="h",
            thickness=14,
            len=0.45,
            x=0.5,
            xanchor="center",
            y=0.03,
            yanchor="bottom",
            bgcolor="rgba(255,255,255,0.8)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


@st.cache_data(show_spinner="Armando el mapa animado...")
def build_hhi_animated_map(_geojson, df, hhi_min, hhi_max, height):
    fig = px.choropleth_map(
        df,
        geojson=_geojson,
        locations="provincia",
        featureidkey="properties.provincia",
        color="hhi",
        animation_frame="anio",
        color_continuous_scale="YlOrRd",
        range_color=(hhi_min, hhi_max),
        opacity=0.85,
        map_style=MAPBOX_STYLE,
        center=MAP_CENTER,
        zoom=MAP_ZOOM,
        hover_name="provincia",
        hover_data={"provincia": False, "anio": False, "hhi": ":.3f"},
        labels={"hhi": "Índice de concentración (HHI)"},
    )
    fig.update_traces(marker_line_width=0.6, marker_line_color="white")
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        font=dict(family=FONT_FAMILY, size=13, color=TEXT_COLOR),
        coloraxis_colorbar=dict(
            title=dict(text="HHI (concentración sectorial)", side="top", font=dict(color=TEXT_COLOR, size=12)),
            tickfont=dict(color=TEXT_COLOR, size=11),
            orientation="h",
            thickness=14,
            len=0.45,
            x=0.5,
            xanchor="center",
            y=0.10,
            yanchor="bottom",
            bgcolor="rgba(255,255,255,0.8)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    # Slider y botón de play dentro del mapa, abajo, con fondo semitransparente
    # px incrusta el geojson completo (~880KB) en CADA uno de los 21 frames
    # (~17MB en total). Los frames solo necesitan actualizar los valores de
    # color: al quitarles el geojson, la traza base lo conserva y el payload
    # baja a menos de 1MB.
    for frame in fig.frames:
        for tr in frame.data:
            tr.geojson = None

    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].update(
            x=0.20, y=0.03, xanchor="right", yanchor="bottom",
            font=dict(color=TEXT_COLOR),
            bgcolor="rgba(255,255,255,0.85)",
        )
    if fig.layout.sliders:
        fig.layout.sliders[0].update(
            x=0.5, y=0.03, xanchor="center", yanchor="bottom", len=0.55,
            currentvalue=dict(prefix="Año: ", font=dict(family=FONT_FAMILY, size=14, color=TEXT_COLOR)),
            font=dict(family=FONT_FAMILY, color=TEXT_COLOR),
            bgcolor="rgba(200,200,200,0.6)",
            bordercolor="rgba(255,255,255,0.9)",
            pad=dict(t=0, b=0),
        )
    return fig


# ---------------------------------------------------------------------------
# KPIs nacionales
# ---------------------------------------------------------------------------
vab_pais = vab_total.groupby("anio")["vab"].sum()
crecimiento_nacional = 100 * (vab_pais.loc[2022] / vab_pais.loc[2004] - 1)
mas_crecio = crecimiento.loc[crecimiento["crecimiento_acumulado_pct"].idxmax()]
menos_crecio = crecimiento.loc[crecimiento["crecimiento_acumulado_pct"].idxmin()]
hhi_2024 = hhi[hhi["anio"] == 2024]
mas_concentrada = hhi_2024.loc[hhi_2024["hhi"].idxmax()]

# ---------------------------------------------------------------------------
# MAPA a pantalla completa (se dibuja primero; las tarjetas van encima)
# ---------------------------------------------------------------------------
vista = st.session_state.get("vista", VISTA_CRECIMIENTO)

provincia_seleccionada = None
with st.container(key="map_full"):
    if vista == VISTA_CRECIMIENTO:
        fig = build_growth_map(geojson, crecimiento, MAP_HEIGHT)
        evento = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="mapa_crecimiento",
            config={"displayModeBar": False},
        )
        puntos = evento.get("selection", {}).get("points", []) if evento else []
        provincia_seleccionada = puntos[0].get("location") if puntos else "Neuquén"
        seleccion_por_click = bool(puntos)
    else:
        fig = build_hhi_animated_map(
            geojson, hhi.sort_values("anio"), hhi["hhi"].min(), hhi["hhi"].max(), MAP_HEIGHT
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="mapa_hhi",
            config={"displayModeBar": False},
        )

# ---------------------------------------------------------------------------
# HUD IZQUIERDO: título, selector de vista, KPIs, ranking, fuente
# ---------------------------------------------------------------------------
with st.container(key="hud_left"):
    st.markdown("### ¿Cómo le fue a cada provincia desde 2004?")
    st.caption(
        "Crecimiento del VAB por jurisdicción (2004-2024), su estructura "
        "sectorial y el contexto detrás de seis casos destacados."
    )

    st.segmented_control(
        "Vista",
        options=[VISTA_CRECIMIENTO, VISTA_HHI],
        default=VISTA_CRECIMIENTO,
        key="vista",
        label_visibility="collapsed",
    )

    st.markdown(
        f"**🇦🇷 País (2004-2022):** +{crecimiento_nacional:.1f}%  \n"
        f"**📈 Mayor crecimiento:** {mas_crecio['provincia']} (+{mas_crecio['crecimiento_acumulado_pct']:.0f}%)  \n"
        f"**📉 Menor crecimiento:** {menos_crecio['provincia']} ({menos_crecio['crecimiento_acumulado_pct']:.1f}%)  \n"
        f"**🎯 Más concentrada (2024):** {mas_concentrada['provincia']} (HHI {mas_concentrada['hhi']:.2f})"
    )

    st.markdown("##### 🏆 Ranking de crecimiento 2004-2022")
    ranking = crecimiento.sort_values("crecimiento_acumulado_pct", ascending=True)
    fig_ranking = px.bar(
        ranking,
        x="crecimiento_acumulado_pct",
        y="provincia",
        orientation="h",
        color="crecimiento_acumulado_pct",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        labels={"crecimiento_acumulado_pct": "%", "provincia": ""},
    )
    fig_ranking.update_layout(
        margin=dict(l=0, r=0, t=5, b=0),
        height=430,
        font=dict(family=FONT_FAMILY, size=11, color=TEXT_COLOR),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(127,127,127,0.15)"),
    )
    st.plotly_chart(fig_ranking, use_container_width=True, config={"displayModeBar": False})

    st.caption(
        "Fuente: CEPAL/MECON, \"Desagregación provincial del VAB de la Argentina, "
        "base 2004\" (LC/TS.2022/196), 2022. Límites: IGN."
    )

# ---------------------------------------------------------------------------
# HUD DERECHO: detalle de la provincia seleccionada (solo vista crecimiento)
# ---------------------------------------------------------------------------
if vista == VISTA_CRECIMIENTO and provincia_seleccionada:
    with st.container(key="hud_right"):
        if not seleccion_por_click:
            st.caption("Mostrando Neuquén de ejemplo — hacé click en cualquier provincia.")
        st.markdown(f"### {provincia_seleccionada}")

        fila = crecimiento[crecimiento["provincia"] == provincia_seleccionada].iloc[0]
        c1, c2 = st.columns(2)
        c1.metric(
            f"Crecimiento {fila['anio_inicial']}-{fila['anio_final']}",
            f"{fila['crecimiento_acumulado_pct']:.1f}%",
        )
        c2.metric("Anual promedio", f"{fila['crecimiento_anual_promedio_pct']:.1f}%")

        serie = vab_total[vab_total["provincia"] == provincia_seleccionada].sort_values("anio")
        fig_linea = go.Figure()
        fig_linea.add_trace(
            go.Scatter(
                x=serie["anio"],
                y=serie["vab"],
                mode="lines+markers",
                marker=dict(
                    size=6,
                    color=[
                        "#d62728" if n != "definitivo" else "#1f77b4"
                        for n in serie["nota_calidad"]
                    ],
                ),
                line=dict(color="#1f77b4", width=2),
                name="VAB total",
            )
        )
        fig_linea.update_layout(
            title=dict(text="Evolución del VAB (millones de $ ctes. 2004)", font=dict(size=13)),
            margin=dict(l=0, r=0, t=35, b=0),
            height=210,
            showlegend=False,
            font=dict(family=FONT_FAMILY, size=11, color=TEXT_COLOR),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(127,127,127,0.15)"),
        )
        st.plotly_chart(fig_linea, use_container_width=True, config={"displayModeBar": False})
        st.caption("Rojo: datos provisorios (2023) o preliminares (2024).")

        est_prov = estructura[estructura["provincia"] == provincia_seleccionada]

        st.markdown("##### 🔬 Desagregación por macro-sector, año a año")
        anio_detalle = st.selectbox(
            "Año",
            sorted(est_prov["anio"].unique(), reverse=True),
            key="anio_detalle",
        )
        detalle = est_prov[est_prov["anio"] == anio_detalle].sort_values(
            "participacion_pct", ascending=True
        )
        fig_detalle = px.bar(
            detalle,
            x="participacion_pct",
            y="macro_sector",
            orientation="h",
            labels={"participacion_pct": "% del VAB provincial", "macro_sector": ""},
            color_discrete_sequence=["#2563eb"],
            hover_data={"vab": ":.0f"},
        )
        fig_detalle.update_layout(
            margin=dict(l=0, r=0, t=5, b=0),
            height=330,
            font=dict(family=FONT_FAMILY, size=11, color=TEXT_COLOR),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="rgba(127,127,127,0.15)"),
        )
        st.plotly_chart(fig_detalle, use_container_width=True, config={"displayModeBar": False})
        st.caption("Los 11 macro-sectores, ordenados por peso en el año elegido.")

        if provincia_seleccionada in CASOS_DESTACADOS:
            caso = CASOS_DESTACADOS[provincia_seleccionada]
            st.markdown("---")
            st.markdown(f"#### 📖 {caso['titulo']}")
            st.markdown(caso["texto"])
            st.caption(f"Fuentes: {caso['fuente']}")
