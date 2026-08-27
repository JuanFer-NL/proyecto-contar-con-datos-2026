-- Esquema de la base de datos del proyecto (SQLite)
-- Fuente de datos: CEPAL/MECON, "Desagregación provincial del VAB de la Argentina, base 2004"

CREATE TABLE IF NOT EXISTS provincias (
    id            INTEGER PRIMARY KEY,
    nombre        TEXT NOT NULL UNIQUE,   -- nombre canónico, igual al usado en los CSV tidy
    codigo_indec  TEXT,                   -- código de provincia INDEC (2 dígitos), para el join con el shapefile del IGN
    region        TEXT                    -- NOA, NEA, Cuyo, Centro, Patagonia, CABA+GBA (agrupación propia, a definir)
);

CREATE TABLE IF NOT EXISTS sectores (
    id            INTEGER PRIMARY KEY,
    nombre        TEXT NOT NULL UNIQUE,   -- una de las 52 ramas CIIU Rev. 3.1, tal como está en el Excel fuente
    macro_sector  TEXT                    -- agrupación propia en ~8-10 categorías legibles (agro, industria, energía, servicios, etc.)
);

CREATE TABLE IF NOT EXISTS vab_total (
    provincia_id  INTEGER NOT NULL REFERENCES provincias(id),
    anio          INTEGER NOT NULL,
    vab           REAL NOT NULL,          -- millones de pesos constantes de 2004
    nota_calidad  TEXT NOT NULL,          -- definitivo | provisorio | preliminar
    PRIMARY KEY (provincia_id, anio)
);

CREATE TABLE IF NOT EXISTS vab_sectorial (
    provincia_id  INTEGER NOT NULL REFERENCES provincias(id),
    sector_id     INTEGER NOT NULL REFERENCES sectores(id),
    anio          INTEGER NOT NULL,
    vab           REAL NOT NULL,          -- millones de pesos constantes de 2004
    nota_calidad  TEXT NOT NULL,
    PRIMARY KEY (provincia_id, sector_id, anio)
);

CREATE INDEX IF NOT EXISTS idx_vab_total_anio ON vab_total(anio);
CREATE INDEX IF NOT EXISTS idx_vab_sectorial_anio ON vab_sectorial(anio);
CREATE INDEX IF NOT EXISTS idx_vab_sectorial_sector ON vab_sectorial(sector_id);
