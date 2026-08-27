"""
Descarga la capa "Provincia" del IGN (WFS) y genera un GeoJSON simplificado
listo para usar en el mapa interactivo.

Fuente: Instituto Geográfico Nacional (IGN), capa "Provincia".
https://www.ign.gob.ar/NuestrasActividades/InformacionGeoespacial/CapasSIG

Salida: data/processed/provincias.geojson
"""

from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import requests

WFS_URL = (
    "https://wms.ign.gob.ar/geoserver/ign/ows"
    "?service=WFS&version=1.0.0&request=GetFeature"
    "&typeName=ign%3Aprovincia&outputFormat=SHAPE-ZIP"
)

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "shapefile_provincias"
OUT_PATH = ROOT / "data" / "processed" / "provincias.geojson"

SIMPLIFY_TOLERANCE = 0.01  # grados (~1 km) — suficiente para un mapa a nivel provincial


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "provincia.zip"

    print("Descargando shapefile del IGN...")
    resp = requests.get(WFS_URL, timeout=120)
    resp.raise_for_status()
    zip_path.write_bytes(resp.content)

    with ZipFile(zip_path) as zf:
        zf.extractall(RAW_DIR)

    shp_path = RAW_DIR / "provinciaPolygon.shp"
    gdf = gpd.read_file(shp_path)
    gdf = gdf.rename(columns={"nam": "provincia", "in1": "codigo_indec"})[
        ["provincia", "codigo_indec", "geometry"]
    ]
    gdf["geometry"] = gdf["geometry"].simplify(
        tolerance=SIMPLIFY_TOLERANCE, preserve_topology=True
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OUT_PATH.exists():
        OUT_PATH.unlink()
    gdf.to_file(OUT_PATH, driver="GeoJSON")

    print(f"OK: {len(gdf)} provincias -> {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
