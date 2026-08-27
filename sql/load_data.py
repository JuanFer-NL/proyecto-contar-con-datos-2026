"""
Carga los CSV tidy (generados por etl/build_tidy_dataset.py) a una base SQLite
siguiendo el esquema definido en sql/schema.sql.

Uso: python sql/load_data.py
Genera: data/processed/contar_con_datos.db
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DB_PATH = PROCESSED_DIR / "contar_con_datos.db"

# Código de provincia INDEC (2 dígitos) por nombre canónico.
# Referencia: Codificador de provincias INDEC.
CODIGO_INDEC = {
    "Ciudad Autónoma de Buenos Aires": "02",
    "Buenos Aires": "06",
    "Catamarca": "10",
    "Córdoba": "14",
    "Corrientes": "18",
    "Chaco": "22",
    "Chubut": "26",
    "Entre Ríos": "30",
    "Formosa": "34",
    "Jujuy": "38",
    "La Pampa": "42",
    "La Rioja": "46",
    "Mendoza": "50",
    "Misiones": "54",
    "Neuquén": "58",
    "Río Negro": "62",
    "Salta": "66",
    "San Juan": "70",
    "San Luis": "74",
    "Santa Cruz": "78",
    "Santa Fe": "82",
    "Santiago del Estero": "86",
    "Tucumán": "90",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "94",
}


def main():
    vab_total = pd.read_csv(PROCESSED_DIR / "vab_total.csv")
    vab_sectorial = pd.read_csv(PROCESSED_DIR / "vab_sectorial.csv")

    # Solo las 24 jurisdicciones reales van a la tabla de dimensión "provincias".
    provincias = sorted(vab_total.loc[vab_total["es_jurisdiccion"], "provincia"].unique())
    sectores = sorted(vab_sectorial["sector"].unique())

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    conn.executemany(
        "INSERT INTO provincias (nombre, codigo_indec) VALUES (?, ?)",
        [(p, CODIGO_INDEC.get(p)) for p in provincias],
    )
    conn.executemany(
        "INSERT INTO sectores (nombre) VALUES (?)",
        [(s,) for s in sectores],
    )
    conn.commit()

    provincia_id = {
        row[0]: row[1] for row in conn.execute("SELECT nombre, id FROM provincias")
    }
    sector_id = {
        row[0]: row[1] for row in conn.execute("SELECT nombre, id FROM sectores")
    }

    total_rows = [
        (provincia_id[r.provincia], int(r.anio), r.vab, r.nota_calidad)
        for r in vab_total.itertuples()
        if r.es_jurisdiccion
    ]
    conn.executemany(
        "INSERT INTO vab_total (provincia_id, anio, vab, nota_calidad) VALUES (?, ?, ?, ?)",
        total_rows,
    )

    sectorial_rows = [
        (provincia_id[r.provincia], sector_id[r.sector], int(r.anio), r.vab, r.nota_calidad)
        for r in vab_sectorial.itertuples()
    ]
    conn.executemany(
        "INSERT INTO vab_sectorial (provincia_id, sector_id, anio, vab, nota_calidad) VALUES (?, ?, ?, ?, ?)",
        sectorial_rows,
    )

    conn.commit()

    sin_codigo = [p for p in provincias if CODIGO_INDEC.get(p) is None]
    if sin_codigo:
        print(f"ADVERTENCIA: sin código INDEC para: {sin_codigo}")

    print(f"OK: {len(provincias)} provincias, {len(sectores)} sectores")
    print(f"OK: {len(total_rows)} filas en vab_total, {len(sectorial_rows)} filas en vab_sectorial")
    print(f"Base de datos: {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
