-- Esquema de base de datos para control de downtime de centrales telefónicas

CREATE TABLE IF NOT EXISTS centrales (
    codigo      TEXT PRIMARY KEY,
    localidad   TEXT NOT NULL,
    zona        TEXT
);

CREATE TABLE IF NOT EXISTS incidencias (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_central      TEXT NOT NULL REFERENCES centrales(codigo),
    fecha_inicio        TIMESTAMP NOT NULL,
    fecha_fin           TIMESTAMP,
    duracion_minutos    INTEGER,
    estado              TEXT NOT NULL DEFAULT 'ABIERTA', -- ABIERTA | CERRADA
    tecnico_reporta     TEXT,
    tecnico_restablece  TEXT,
    observaciones       TEXT
);

CREATE INDEX IF NOT EXISTS idx_incidencias_central ON incidencias(codigo_central);
CREATE INDEX IF NOT EXISTS idx_incidencias_estado ON incidencias(estado);
