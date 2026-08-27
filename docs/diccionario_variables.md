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

## Notas metodológicas heredadas de la fuente

- **Año base**: 2004. Los valores están a precios constantes de ese año (no corregidos por inflación posterior a 2004, permite comparar volumen físico entre años).
- **Método de estimación**: la CEPAL/MECON parte del PBG oficial 2004 (INDEC) por sector y jurisdicción, y lo extrapola con 52 índices de volumen físico (IVF) específicos por sector (producción física, empleo registrado —OEDE—, patentamientos, gasto público en personal, etc., según el sector). Luego ajustan proporcionalmente para que la suma de las 24 jurisdicciones coincida con el VAB nacional publicado por INDEC.
- **Limitación reconocida por los autores**: esta estimación no reemplaza al PBG oficial de cada Dirección de Estadística provincial, que cuenta con fuentes más precisas y detalladas a nivel local (especialmente en el sector agropecuario). Útil para comparar entre provincias con metodología homogénea, no para reemplazar el dato oficial de una provincia puntual.
- **Actualización**: la serie original se actualiza anualmente en el último trimestre por parte de CEPAL/MECON. Este proyecto usa el corte descargado el 27/08/2026 (ver `data/raw/Jurisdiccion_52sectores.xlsx`).

## Fuente

Equipo de trabajo de la CEPAL y el Ministerio de Economía de la Argentina, "Desagregación provincial del valor agregado bruto de la Argentina, base 2004", *Documentos de Proyectos* (LC/TS.2022/196), Santiago, CEPAL, 2022.
https://www.cepal.org/es/publicaciones/47900-desagregacion-provincial-valor-agregado-bruto-la-argentina-base-2004
