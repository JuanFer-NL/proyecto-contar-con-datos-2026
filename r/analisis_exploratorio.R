# Análisis exploratorio: estructura económica provincial y su evolución
#
# Lee la base SQLite (generada por sql/load_data.py) y calcula las métricas
# derivadas que va a consumir el mapa interactivo:
#   1. Participación % de cada macro-sector en el VAB provincial, por año
#   2. Índice de Herfindahl-Hirschman (HHI) de diversificación productiva
#   3. Tasa de crecimiento acumulada del VAB por provincia, 2004-2024
#
# Salidas (data/processed/):
#   estructura_macrosectorial.csv
#   diversificacion_hhi.csv
#   crecimiento_provincial.csv
#
# Ejecutar desde la raíz del repo: Rscript r/analisis_exploratorio.R

library(DBI)
library(RSQLite)
library(dplyr)
library(tidyr)
library(readr)

DB_PATH <- file.path("data", "processed", "contar_con_datos.db")
OUT_DIR <- file.path("data", "processed")

if (!file.exists(DB_PATH)) {
  stop(sprintf(
    "No se encontró %s. Ejecutar primero: python sql/load_data.py (desde la raíz del repo)",
    DB_PATH
  ))
}

con <- dbConnect(SQLite(), DB_PATH)

vab_sectorial <- dbGetQuery(con, "
  SELECT p.nombre AS provincia, s.macro_sector, v.anio, v.vab
  FROM vab_sectorial v
  JOIN provincias p ON p.id = v.provincia_id
  JOIN sectores s ON s.id = v.sector_id
") |> as_tibble()

vab_total <- dbGetQuery(con, "
  SELECT p.nombre AS provincia, v.anio, v.vab, v.nota_calidad
  FROM vab_total v
  JOIN provincias p ON p.id = v.provincia_id
") |> as_tibble()

dbDisconnect(con)

# 1. Participación % de cada macro-sector en el VAB provincial, por año -----

vab_macrosector <- vab_sectorial |>
  group_by(provincia, macro_sector, anio) |>
  summarise(vab = sum(vab), .groups = "drop")

estructura_macrosectorial <- vab_macrosector |>
  group_by(provincia, anio) |>
  mutate(participacion_pct = 100 * vab / sum(vab)) |>
  ungroup() |>
  arrange(provincia, anio, desc(participacion_pct))

write_csv(estructura_macrosectorial, file.path(OUT_DIR, "estructura_macrosectorial.csv"))
message(sprintf("estructura_macrosectorial.csv: %d filas", nrow(estructura_macrosectorial)))

# 2. Índice de Herfindahl-Hirschman (HHI) de diversificación productiva -----
# HHI = suma de las participaciones (0-1) al cuadrado, por provincia y año.
# HHI cercano a 1/n_sectores -> estructura muy diversificada.
# HHI cercano a 1 -> estructura muy concentrada en pocos sectores.
# Se calcula sobre los 52 sectores originales (no los macro-sectores) para
# no subestimar la concentración real.

diversificacion_hhi <- vab_sectorial |>
  group_by(provincia, anio) |>
  mutate(participacion = vab / sum(vab)) |>
  summarise(hhi = sum(participacion^2), .groups = "drop") |>
  arrange(provincia, anio)

write_csv(diversificacion_hhi, file.path(OUT_DIR, "diversificacion_hhi.csv"))
message(sprintf("diversificacion_hhi.csv: %d filas", nrow(diversificacion_hhi)))

# 3. Tasa de crecimiento acumulada del VAB por provincia, 2004-2024 ---------
# Usa el último año con dato "definitivo" como punto de comparación robusto
# (excluye provisorio/preliminar para no comparar contra una estimación).

anio_base <- min(vab_total$anio)
anio_final_definitivo <- vab_total |>
  filter(nota_calidad == "definitivo") |>
  summarise(m = max(anio)) |>
  pull(m)

crecimiento_provincial <- vab_total |>
  filter(anio %in% c(anio_base, anio_final_definitivo)) |>
  select(provincia, anio, vab) |>
  pivot_wider(names_from = anio, values_from = vab, names_prefix = "vab_") |>
  rename(vab_inicial = !!paste0("vab_", anio_base), vab_final = !!paste0("vab_", anio_final_definitivo)) |>
  mutate(
    anio_inicial = anio_base,
    anio_final = anio_final_definitivo,
    crecimiento_acumulado_pct = 100 * (vab_final / vab_inicial - 1),
    crecimiento_anual_promedio_pct = 100 * ((vab_final / vab_inicial)^(1 / (anio_final_definitivo - anio_base)) - 1)
  ) |>
  arrange(desc(crecimiento_acumulado_pct))

write_csv(crecimiento_provincial, file.path(OUT_DIR, "crecimiento_provincial.csv"))
message(sprintf(
  "crecimiento_provincial.csv: %d filas (comparando %d vs %d)",
  nrow(crecimiento_provincial), anio_base, anio_final_definitivo
))
