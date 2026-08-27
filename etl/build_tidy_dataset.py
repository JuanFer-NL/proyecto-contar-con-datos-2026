"""
ETL: convierte Jurisdiccion_52sectores.xlsx (CEPAL/MECON, VAB provincial base 2004)
de formato ancho (una hoja por provincia, años en columnas) a formato tidy/long,
listo para cargar en SQL y analizar en R.

Fuente: Equipo de trabajo de la CEPAL y el Ministerio de Economía de la Argentina,
"Desagregación provincial del valor agregado bruto de la Argentina, base 2004",
Documentos de Proyectos (LC/TS.2022/196), CEPAL, 2022.

Salidas:
  data/processed/vab_total.csv      -> provincia, anio, vab, nota_calidad
  data/processed/vab_sectorial.csv  -> provincia, sector, anio, vab, nota_calidad
"""

import re
from pathlib import Path

import pandas as pd

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "Jurisdiccion_52sectores.xlsx"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

# Nombre de hoja -> nombre de provincia legible
SHEET_TO_PROVINCIA = {
    "Ciudad_de_Buenos_Aires": "Ciudad Autónoma de Buenos Aires",
    "Buenos_Aires": "Buenos Aires",
    "Catamarca": "Catamarca",
    "Cordoba": "Córdoba",
    "Corrientes": "Corrientes",
    "Chaco": "Chaco",
    "Chubut": "Chubut",
    "Entre_Rios": "Entre Ríos",
    "Formosa": "Formosa",
    "Jujuy": "Jujuy",
    "La_Pampa": "La Pampa",
    "La_Rioja": "La Rioja",
    "Mendoza": "Mendoza",
    "Misiones": "Misiones",
    "Neuquen": "Neuquén",
    "Rio_Negro": "Río Negro",
    "Salta": "Salta",
    "San_Juan": "San Juan",
    "San_Luis": "San Luis",
    "Santa_Cruz": "Santa Cruz",
    "Santa_Fe": "Santa Fe",
    "Santiago_del_Estero": "Santiago del Estero",
    "Tucuman": "Tucumán",
    "Tierra_del_Fuego": "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
}
# "No_distribuido" se excluye: no corresponde a ninguna jurisdicción específica.

# Normaliza las etiquetas de provincia tal como aparecen en la hoja "VABpb"
# (formato levemente distinto al de los nombres de hoja) al nombre canónico.
RAW_LABEL_TO_PROVINCIA = {
    "Ciudad de Buenos Aires": "Ciudad Autónoma de Buenos Aires",
    "Tierra del Fuego": "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
}

HEADER_ROW_IDX = 6  # fila 6 (1-indexed) tiene los encabezados de año / sector
TOTAL_ROW_LABEL = "VAB a precios básicos"


def parse_year_column(col_label):
    """'2023 (1)' -> (2023, 'provisorio'); '2024 (2)' -> (2024, 'preliminar'); 2010 -> (2010, 'definitivo')"""
    label = str(col_label).strip()
    match = re.match(r"(\d{4})\s*(\(\d\))?", label)
    if not match:
        return None, None
    year = int(match.group(1))
    marca = match.group(2)
    nota = {"(1)": "provisorio", "(2)": "preliminar"}.get(marca, "definitivo")
    return year, nota


def build_vab_total():
    df = pd.read_excel(RAW_PATH, sheet_name="VABpb", header=HEADER_ROW_IDX - 1)
    df = df.rename(columns={df.columns[1]: "provincia_raw"})
    df = df.dropna(subset=["provincia_raw"])

    year_cols = [c for c in df.columns if parse_year_column(c)[0] is not None]

    records = []
    for _, row in df.iterrows():
        provincia_raw = str(row["provincia_raw"]).strip()
        if provincia_raw.startswith("("):  # notas al pie
            continue
        provincia = RAW_LABEL_TO_PROVINCIA.get(provincia_raw, provincia_raw)
        for col in year_cols:
            anio, nota = parse_year_column(col)
            valor = row[col]
            if pd.isna(valor):
                continue
            records.append(
                {
                    "provincia": provincia,
                    "anio": anio,
                    "vab": float(valor),
                    "nota_calidad": nota,
                    "es_jurisdiccion": provincia not in ("Total", "No distribuido"),
                }
            )
    return pd.DataFrame.from_records(records)


def build_vab_sectorial():
    all_records = []
    for sheet_name, provincia in SHEET_TO_PROVINCIA.items():
        df = pd.read_excel(RAW_PATH, sheet_name=sheet_name, header=HEADER_ROW_IDX - 1)
        df = df.rename(columns={df.columns[1]: "sector"})
        df = df.dropna(subset=["sector"])

        year_cols = [c for c in df.columns if parse_year_column(c)[0] is not None]

        for _, row in df.iterrows():
            sector = str(row["sector"]).strip()
            if sector == TOTAL_ROW_LABEL or sector.startswith("("):
                continue
            for col in year_cols:
                anio, nota = parse_year_column(col)
                valor = row[col]
                if pd.isna(valor):
                    continue
                all_records.append(
                    {
                        "provincia": provincia,
                        "sector": sector,
                        "anio": anio,
                        "vab": float(valor),
                        "nota_calidad": nota,
                    }
                )
    return pd.DataFrame.from_records(all_records)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    vab_total = build_vab_total()
    vab_total.to_csv(OUT_DIR / "vab_total.csv", index=False)
    print(f"vab_total.csv: {len(vab_total)} filas, {vab_total['provincia'].nunique()} provincias")

    vab_sectorial = build_vab_sectorial()
    vab_sectorial.to_csv(OUT_DIR / "vab_sectorial.csv", index=False)
    print(
        f"vab_sectorial.csv: {len(vab_sectorial)} filas, "
        f"{vab_sectorial['provincia'].nunique()} provincias, "
        f"{vab_sectorial['sector'].nunique()} sectores"
    )


if __name__ == "__main__":
    main()
