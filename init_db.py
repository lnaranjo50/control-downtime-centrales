"""
Inicializa la base de datos SQLite y carga el catálogo de centrales
extraído de "Estadistica de Central LPU MES DE ABRIL 2026.xls".

Ejecutar una sola vez (o cada vez que quieras resetear el catálogo):
    python init_db.py
"""

import sqlite3

DB_PATH = "downtime.db"

CENTRALES = [
    {"Localidad": "LA PUERTA", "Codigo": "LPU"},
    {"Localidad": "AGUA CALIENTE", "Codigo": "ACAL"},
    {"Localidad": "SAN NICOLAS", "Codigo": "SANN"},
    {"Localidad": "TRINIDAD", "Codigo": "TRNI"},
    {"Localidad": "VILLANUEVA II", "Codigo": "VILL"},
    {"Localidad": "SANTA CRUZ DE YOJOA", "Codigo": "SCYO"},
    {"Localidad": "QUIMISTAN", "Codigo": "QUIM"},
    {"Localidad": "PINALEJO", "Codigo": "PINA"},
    {"Localidad": "SAN MARCOS OCOTEPEQUE", "Codigo": "SMOC"},
    {"Localidad": "LA LABOR", "Codigo": "LAB"},
    {"Localidad": "SAN FRANCISCO VALLE", "Codigo": "SFV"},
    {"Localidad": "EL NEGRITO", "Codigo": "ELNE"},
    {"Localidad": "MORAZAN", "Codigo": "MORA"},
    {"Localidad": "TAULABE", "Codigo": "TBE"},
    {"Localidad": "SAN JOSE COLINAS", "Codigo": "SJOC"},
    {"Localidad": "SANTA MARTHA", "Codigo": "SMAT"},
    {"Localidad": "RUINAS", "Codigo": "COPA"},
    {"Localidad": "SAN ANTONIO", "Codigo": "SAC"},
    {"Localidad": "ANTIGUA OCOTEPEQUE", "Codigo": "AOCO"},
    {"Localidad": "ELCATEX", "Codigo": "ZCHO"},
    {"Localidad": "SAN LUIS", "Codigo": "SLUI"},
    {"Localidad": "FLORIDA", "Codigo": "FLOD"},
    {"Localidad": "NACO", "Codigo": "NACO"},
    {"Localidad": "PEÑA BLANCA", "Codigo": "PEÑA"},
    {"Localidad": "OCOTEPEQUE", "Codigo": "NUOC"},
    {"Localidad": "ENTRADA", "Codigo": "ECOP"},
    {"Localidad": "RES. LAS COLINAS", "Codigo": "LCOL"},
    {"Localidad": "SULA", "Codigo": "SULA"},
    {"Localidad": "PIMIENTA", "Codigo": "PIM"},
    {"Localidad": "CGRACIAS", "Codigo": "GRA"},
    {"Localidad": "BRISAS DEL VALLE", "Codigo": "LBRI"},
    {"Localidad": "MACKEY", "Codigo": "MCKY"},
    {"Localidad": "STIBYS", "Codigo": "STBY"},
    {"Localidad": "NOVA", "Codigo": "NOVA"},
    {"Localidad": "SITRATEL", "Codigo": "SITR"},
    {"Localidad": "ZIP BUENA VISTA", "Codigo": "ZBVI"},  # corregido: venía como "Boom" en el origen
    {"Localidad": "CAMPISA", "Codigo": "CAPI"},
    {"Localidad": "VILLAS PARAISO", "Codigo": "VPAR"},
    {"Localidad": "LOMAS DE SAN JUAN", "Codigo": "LSJU"},
    {"Localidad": "LA TRINIDAD", "Codigo": "LTRI"},
    {"Localidad": "USULA", "Codigo": "USUL"},
    {"Localidad": "BUFALO", "Codigo": "BUFA"},
    {"Localidad": "PARAISO COPAN", "Codigo": "EPAR"},
    {"Localidad": "REAL DEL PUENTE", "Codigo": "REAL"},
    {"Localidad": "SPS CENTRO 2", "Codigo": "SCE2"},
    {"Localidad": "SPS CENTRO 3", "Codigo": "SCE3"},
    {"Localidad": "LA FLORIDA", "Codigo": "LFLO"},
    {"Localidad": "JUAN LINDO", "Codigo": "LIND"},
    {"Localidad": "SPS CENTRO 4", "Codigo": "SCE4"},
    {"Localidad": "SPS CENTRO 5", "Codigo": "SCE5"},
    {"Localidad": "MONTE MARIA", "Codigo": "MMAR"},
    {"Localidad": "LA GRAN VILLA", "Codigo": "GVIA"},
    {"Localidad": "BOSQUES DE JUCUTUMA", "Codigo": "BJUC"},
    {"Localidad": "SAN JUAN LIMA", "Codigo": "SAJU"},
    {"Localidad": "SPS CENTRO 1", "Codigo": "SCE1"},
    {"Localidad": "SAN FRANCISCO YOJOA", "Codigo": "SFRI"},
    {"Localidad": "LAGO DE YOJOA", "Codigo": "LYOJ"},
    {"Localidad": "EL PROGRESO", "Codigo": "EPRO"},
    {"Localidad": "SAN PEDRO COPAN", "Codigo": "SPC"},
    {"Localidad": "SANTA BARBARA", "Codigo": "SBAR"},
    {"Localidad": "SANTA ROSA DE COPAN", "Codigo": "SRC"},
]


def main():
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    for c in CENTRALES:
        cur.execute(
            "INSERT OR IGNORE INTO centrales (codigo, localidad) VALUES (?, ?)",
            (c["Codigo"], c["Localidad"]),
        )
    conn.commit()

    total = cur.execute("SELECT COUNT(*) FROM centrales").fetchone()[0]
    print(f"Base de datos inicializada en '{DB_PATH}'. Centrales cargadas: {total}")
    conn.close()


if __name__ == "__main__":
    main()
