# Diccionario de Variables

## `data/processed/vab_total.csv`

| Variable | Tipo | Descripción |
|---|---|---|
| `provincia` | texto | Nombre de la jurisdicción. Incluye 24 provincias/CABA, más `Total` (país) y `No distribuido` (VAB no asignable a ninguna jurisdicción). |
| `anio` | entero | Año calendario, 2004–2024. |
| `vab` | numérico | Valor Agregado Bruto a precios básicos, en millones de pesos constantes de 2004. |
| `nota_calidad` | texto | `definitivo`, `provisorio` (2023) o `preliminar` (2024). |
| `es_jurisdiccion` | booleano | `False` para las filas `Total` y `No distribuido`; `True` para las 24 jurisdicciones reales. Filtrar por `True` para mapear. |

## `data/processed/vab_sectorial.csv`

| Variable | Tipo | Descripción |
|---|---|---|
| `provincia` | texto | Una de las 24 jurisdicciones (sin `Total` ni `No distribuido`). |
| `sector` | texto | Rama de actividad económica, una de 52 categorías según CIIU Revisión 3.1. |
| `anio` | entero | Año calendario, 2004–2024. |
| `vab` | numérico | Valor Agregado Bruto a precios básicos del sector en esa provincia y año, en millones de pesos constantes de 2004. |
| `nota_calidad` | texto | `definitivo`, `provisorio` (2023) o `preliminar` (2024). |

**Control de calidad**: para cada provincia y año, la suma de `vab` sobre los 52 sectores coincide (a error de punto flotante) con el `vab` de `vab_total.csv` para esa misma provincia/año. Verificado en `etl/build_tidy_dataset.py`.

## `data/processed/provincias.geojson`

| Campo | Tipo | Descripción |
|---|---|---|
| `provincia` | texto | Nombre canónico de la provincia, idéntico al usado en `vab_total.csv` / `vab_sectorial.csv` (verificado por match exacto de conjuntos, sin necesidad de tabla de equivalencias). |
| `codigo_indec` | texto | Código de provincia INDEC (2 dígitos), igual al usado en `sql/load_data.py`. |
| `geometry` | polígono | Límite provincial, CRS EPSG:4326 (WGS84), geometría simplificada (tolerancia 0.01°, ~1 km) para uso en mapas web. |

**Fuente**: Instituto Geográfico Nacional (IGN), capa "Provincia", vía servicio WFS del Geoserver del IGN. Generado con `etl/download_shapefile.py`. El shapefile original (sin simplificar, ~64 MB) queda en `data/raw/shapefile_provincias/` y no se versiona en el repo.

## `data/processed/estructura_macrosectorial.csv`

Agrupa los 52 sectores en 11 macro-sectores legibles (ver `sql/macro_sectores.csv` para el mapeo completo, criterio propio del proyecto) y calcula la participación porcentual de cada uno en el VAB provincial de cada año.

| Variable | Tipo | Descripción |
|---|---|---|
| `provincia`, `anio` | — | Igual que en los datasets anteriores. |
| `macro_sector` | texto | Uno de: Agro/pesca/silvicultura, Minería y energía, Industria manufacturera, Construcción, Comercio, Hotelería y gastronomía, Transporte y comunicaciones, Servicios financieros e inmobiliarios, Administración pública/salud/educación, Otros servicios, Resto/no clasificado. |
| `vab` | numérico | VAB del macro-sector (suma de sus sectores componentes). |
| `participacion_pct` | numérico | % que representa ese macro-sector sobre el VAB total de la provincia en ese año. Suma 100% por provincia/año. |

**Nota**: "Resto/no clasificado" corresponde al sector "Resto" original del dataset fuente (no especificado por CEPAL/MECON) y puede tener peso significativo en algunas jurisdicciones (ej. ~18% en CABA en 2024) — se mantiene sin desagregar por transparencia, no se fuerza su reasignación a otro macro-sector.

Generado por `r/analisis_exploratorio.R`.

## `data/processed/diversificacion_hhi.csv`

Índice de Herfindahl-Hirschman (HHI) de concentración/diversificación productiva, calculado sobre los 52 sectores originales (no los macro-sectores, para no subestimar la concentración real).

| Variable | Tipo | Descripción |
|---|---|---|
| `provincia`, `anio` | — | Igual que en los datasets anteriores. |
| `hhi` | numérico (0-1) | Suma de las participaciones sectoriales al cuadrado. Valores cercanos a 1/52 (~0.02) indican estructura muy diversificada; valores altos (ej. >0.15) indican fuerte concentración en pocos sectores. |

Generado por `r/analisis_exploratorio.R`.

## `data/processed/crecimiento_provincial.csv`

Tasa de crecimiento del VAB total por provincia, comparando el año base (2004) contra el último año con dato **definitivo** (excluye 2023 provisorio y 2024 preliminar para no comparar contra una estimación).

| Variable | Tipo | Descripción |
|---|---|---|
| `provincia` | texto | — |
| `anio_inicial`, `anio_final` | entero | 2004 y el último año definitivo disponible (actualmente 2022). |
| `vab_inicial`, `vab_final` | numérico | VAB total en esos años. |
| `crecimiento_acumulado_pct` | numérico | Variación % total del período. |
| `crecimiento_anual_promedio_pct` | numérico | Tasa de crecimiento anual compuesta equivalente. |

Generado por `r/analisis_exploratorio.R`.

## Notas metodológicas heredadas de la fuente

- **Año base**: 2004. Los valores están a precios constantes de ese año (no corregidos por inflación posterior a 2004, permite comparar volumen físico entre años).
- **Método de estimación**: la CEPAL/MECON parte del PBG oficial 2004 (INDEC) por sector y jurisdicción, y lo extrapola con 52 índices de volumen físico (IVF) específicos por sector (producción física, empleo registrado —OEDE—, patentamientos, gasto público en personal, etc., según el sector). Luego ajustan proporcionalmente para que la suma de las 24 jurisdicciones coincida con el VAB nacional publicado por INDEC.
- **Limitación reconocida por los autores**: esta estimación no reemplaza al PBG oficial de cada Dirección de Estadística provincial, que cuenta con fuentes más precisas y detalladas a nivel local (especialmente en el sector agropecuario). Útil para comparar entre provincias con metodología homogénea, no para reemplazar el dato oficial de una provincia puntual.
- **Actualización**: la serie original se actualiza anualmente en el último trimestre por parte de CEPAL/MECON. Este proyecto usa el corte descargado el 27/08/2026 (ver `data/raw/Jurisdiccion_52sectores.xlsx`).

## Fuente

Equipo de trabajo de la CEPAL y el Ministerio de Economía de la Argentina, "Desagregación provincial del valor agregado bruto de la Argentina, base 2004", *Documentos de Proyectos* (LC/TS.2022/196), Santiago, CEPAL, 2022.
https://www.cepal.org/es/publicaciones/47900-desagregacion-provincial-valor-agregado-bruto-la-argentina-base-2004
