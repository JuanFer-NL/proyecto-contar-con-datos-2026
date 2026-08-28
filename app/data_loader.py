"""Carga de los datasets procesados, con caching de Streamlit."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@st.cache_data
def load_geojson():
    with open(DATA_DIR / "provincias.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_vab_total():
    df = pd.read_csv(DATA_DIR / "vab_total.csv")
    return df[df["es_jurisdiccion"]].drop(columns="es_jurisdiccion")


@st.cache_data
def load_estructura_macrosectorial():
    return pd.read_csv(DATA_DIR / "estructura_macrosectorial.csv")


@st.cache_data
def load_diversificacion_hhi():
    return pd.read_csv(DATA_DIR / "diversificacion_hhi.csv")


@st.cache_data
def load_crecimiento_provincial():
    return pd.read_csv(DATA_DIR / "crecimiento_provincial.csv")
