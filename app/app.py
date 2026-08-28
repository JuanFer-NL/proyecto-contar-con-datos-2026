"""
Mapa interactivo de la estructura económica provincial de Argentina (2004-2024).

Concurso Nacional de Visualización de Datos 2026 — "Contar con Datos"
Categoría: Exploración interactiva

Fuente de datos: CEPAL/MECON, "Desagregación provincial del VAB de la
Argentina, base 2004" (2022). Ver docs/diccionario_variables.md.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
)

geojson = load_geojson()
vab_total = load_vab_total()
estructura = load_estructura_macrosectorial()
hhi = load_diversificacion_hhi()
crecimiento = load_crecimiento_provincial()

ANIO_MIN = int(vab_total["anio"].min())
ANIO_MAX = int(vab_total["anio"].max())

# ---------------------------------------------------------------------------
st.title("¿Cómo le fue a cada provincia argentina desde 2004?")
st.markdown(
    "Un mapa para explorar el crecimiento del Valor Agregado Bruto (VAB) de las "
    "24 jurisdicciones argentinas entre 2004 y 2024, cómo cambió (o no) su "
    "estructura sectorial, y el contexto histórico detrás de los seis casos "
    "más marcados."
)

tab_crecimiento, tab_estructura = st.tabs(
    ["📈 Crecimiento 2004–2022", "🧩 Estructura sectorial en el tiempo"]
)

# ---------------------------------------------------------------------------
# TAB 1: Mapa de crecimiento + panel de detalle por provincia
# ---------------------------------------------------------------------------
with tab_crecimiento:
    col_mapa, col_panel = st.columns([3, 2])

    with col_mapa:
        fig = px.choropleth(
            crecimiento,
            geojson=geojson,
            locations="provincia",
            featureidkey="properties.provincia",
            color="crecimiento_acumulado_pct",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
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
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=600)

        evento = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="mapa_crecimiento",
        )

    provincia_seleccionada = None
    puntos = evento.get("selection", {}).get("points", []) if evento else []
    if puntos:
        provincia_seleccionada = puntos[0].get("location")

    with col_panel:
        if not provincia_seleccionada:
            st.info("👈 Hacé click en una provincia del mapa para ver su detalle.")
        else:
            st.subheader(provincia_seleccionada)

            fila = crecimiento[crecimiento["provincia"] == provincia_seleccionada].iloc[0]
            c1, c2 = st.columns(2)
            c1.metric(
                f"Crecimiento acumulado {fila['anio_inicial']}-{fila['anio_final']}",
                f"{fila['crecimiento_acumulado_pct']:.1f}%",
            )
            c2.metric("Crecimiento anual promedio", f"{fila['crecimiento_anual_promedio_pct']:.1f}%")

            # Evolución del VAB total, marcando datos provisorios/preliminares
            serie = vab_total[vab_total["provincia"] == provincia_seleccionada].sort_values("anio")
            fig_linea = go.Figure()
            fig_linea.add_trace(
                go.Scatter(
                    x=serie["anio"],
                    y=serie["vab"],
                    mode="lines+markers",
                    marker=dict(
                        color=[
                            "#d62728" if n != "definitivo" else "#1f77b4"
                            for n in serie["nota_calidad"]
                        ]
                    ),
                    line=dict(color="#1f77b4"),
                    name="VAB total",
                )
            )
            fig_linea.update_layout(
                title="Evolución del VAB total (millones de $ constantes de 2004)",
                margin=dict(l=0, r=0, t=40, b=0),
                height=280,
                showlegend=False,
            )
            st.plotly_chart(fig_linea, use_container_width=True)
            st.caption("En rojo: datos provisorios (2023) o preliminares (2024).")

            # Composición sectorial: año base vs. último año disponible
            est_prov = estructura[estructura["provincia"] == provincia_seleccionada]
            anio_reciente = int(est_prov["anio"].max())
            comparacion = est_prov[est_prov["anio"].isin([ANIO_MIN, anio_reciente])]

            fig_barras = px.bar(
                comparacion,
                x="participacion_pct",
                y="macro_sector",
                color="anio",
                barmode="group",
                orientation="h",
                labels={
                    "participacion_pct": "% del VAB provincial",
                    "macro_sector": "",
                    "anio": "Año",
                },
                title=f"Composición sectorial: {ANIO_MIN} vs. {anio_reciente}",
            )
            fig_barras.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=380)
            st.plotly_chart(fig_barras, use_container_width=True)

            # Contexto histórico, solo para los 6 casos destacados
            if provincia_seleccionada in CASOS_DESTACADOS:
                caso = CASOS_DESTACADOS[provincia_seleccionada]
                st.markdown("---")
                st.markdown(f"### 📖 {caso['titulo']}")
                st.markdown(caso["texto"])
                st.caption(f"Fuentes: {caso['fuente']}")

# ---------------------------------------------------------------------------
# TAB 2: Estructura sectorial y concentración a lo largo del tiempo
# ---------------------------------------------------------------------------
with tab_estructura:
    anio_seleccionado = st.slider(
        "Año", min_value=ANIO_MIN, max_value=ANIO_MAX, value=ANIO_MIN, step=1
    )

    hhi_anio = hhi[hhi["anio"] == anio_seleccionado]

    fig_hhi = px.choropleth(
        hhi_anio,
        geojson=geojson,
        locations="provincia",
        featureidkey="properties.provincia",
        color="hhi",
        color_continuous_scale="Oranges",
        range_color=(hhi["hhi"].min(), hhi["hhi"].max()),
        hover_name="provincia",
        hover_data={"provincia": False, "hhi": ":.3f"},
        labels={"hhi": "Índice de concentración (HHI)"},
    )
    fig_hhi.update_geos(fitbounds="locations", visible=False)
    fig_hhi.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=600)

    st.plotly_chart(fig_hhi, use_container_width=True)
    st.caption(
        "El índice de Herfindahl-Hirschman (HHI) mide qué tan concentrada está la "
        "economía provincial en pocos sectores (calculado sobre los 52 sectores "
        "originales). Valores más altos y en tonos más oscuros = mayor concentración. "
        f"Escala fija ({hhi['hhi'].min():.3f}–{hhi['hhi'].max():.3f}) para comparar entre años."
    )

st.markdown("---")
st.caption(
    "Fuente: Equipo de trabajo de la CEPAL y el Ministerio de Economía de la Argentina, "
    "\"Desagregación provincial del valor agregado bruto de la Argentina, base 2004\", "
    "Documentos de Proyectos (LC/TS.2022/196), CEPAL, 2022. "
    "Límites provinciales: Instituto Geográfico Nacional (IGN)."
)
