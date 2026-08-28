# Mapa Interactivo de Estructura Económica Provincial

Proyecto presentado al Concurso Nacional de Visualización de Datos 2026 — "Contar con Datos" (categoría: Exploración interactiva).

## Objetivo

Visualizar la estructura económica de cada provincia argentina y su evolución en el tiempo, a partir de la desagregación provincial del Valor Agregado Bruto (VAB) por sector de actividad.

## Fuente de datos

Equipo de trabajo de la CEPAL y el Ministerio de Economía de la Argentina, "Desagregación provincial del valor agregado bruto de la Argentina, base 2004", *Documentos de Proyectos* (LC/TS.2022/196), Santiago, CEPAL, 2022.

https://www.cepal.org/es/publicaciones/47900-desagregacion-provincial-valor-agregado-bruto-la-argentina-base-2004

Datos: VAB a precios básicos (precios constantes de 2004), 24 jurisdicciones, 52 ramas de actividad económica (CIIU Rev. 3.1), serie 2004-2024 (2023 provisorio, 2024 preliminar).

## Estructura del repositorio

```
data/raw/         Datos originales sin modificar
data/processed/   Datos procesados listos para el análisis y la app
sql/              Esquema y scripts de carga de la base de datos
r/                Scripts de análisis exploratorio y cálculo de métricas
app/              Aplicación del mapa interactivo (Python)
docs/             Diccionario de variables, notas metodológicas
```

## Cómo correr el proyecto localmente

```bash
python3 -m venv .venv && source .venv/bin/activate   # o el venv que prefieras
pip install -r etl/requirements.txt -r app/requirements.txt

# Pipeline de datos (ya generado y versionado en data/processed/, re-ejecutar solo si cambia la fuente)
python etl/build_tidy_dataset.py
python etl/download_shapefile.py
python sql/load_data.py
Rscript r/analisis_exploratorio.R

# App
cd app && streamlit run app.py
```

## Licencia y uso

El material presentado a este concurso cede derechos de uso y reproducción a la Secretaría de Innovación, Ciencia y Tecnología de la Nación y a la Universidad de San Andrés, conforme el punto 13 de las Bases y Condiciones del Concurso.
