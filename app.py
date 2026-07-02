"""
Sistema de Control de Downtime de Centrales - MVP con Streamlit + SQLite

Ejecutar con:
    streamlit run app.py
"""

import sqlite3
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

DB_PATH = "downtime.db"

st.set_page_config(page_title="Control de Downtime - Centrales", layout="wide")


def get_conn():
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)


def get_centrales():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT codigo, localidad FROM centrales ORDER BY localidad", conn
    )
    conn.close()
    return df


def registrar_falla(codigo_central, fecha_inicio, tecnico, observaciones):
    conn = get_conn()
    conn.execute(
        """INSERT INTO incidencias (codigo_central, fecha_inicio, estado, tecnico_reporta, observaciones)
           VALUES (?, ?, 'ABIERTA', ?, ?)""",
        (codigo_central, fecha_inicio, tecnico, observaciones),
    )
    conn.commit()
    conn.close()


def get_incidencias_abiertas():
    conn = get_conn()
    df = pd.read_sql_query(
        """SELECT i.id, i.codigo_central, c.localidad, i.fecha_inicio, i.tecnico_reporta
           FROM incidencias i JOIN centrales c ON c.codigo = i.codigo_central
           WHERE i.estado = 'ABIERTA'
           ORDER BY i.fecha_inicio""",
        conn,
    )
    conn.close()
    return df


def registrar_restablecimiento(incidencia_id, fecha_fin, tecnico):
    conn = get_conn()
    row = conn.execute(
        "SELECT fecha_inicio FROM incidencias WHERE id = ?", (incidencia_id,)
    ).fetchone()
    fecha_inicio = datetime.fromisoformat(row[0])
    duracion_min = int((fecha_fin - fecha_inicio).total_seconds() // 60)

    conn.execute(
        """UPDATE incidencias
           SET fecha_fin = ?, duracion_minutos = ?, estado = 'CERRADA', tecnico_restablece = ?
           WHERE id = ?""",
        (fecha_fin, duracion_min, tecnico, incidencia_id),
    )
    conn.commit()
    conn.close()
    return duracion_min


def get_reporte_mensual(anio, mes):
    conn = get_conn()
    df = pd.read_sql_query(
        """SELECT i.codigo_central, c.localidad, i.fecha_inicio, i.fecha_fin, i.duracion_minutos, i.estado
           FROM incidencias i JOIN centrales c ON c.codigo = i.codigo_central
           WHERE strftime('%Y', i.fecha_inicio) = ? AND strftime('%m', i.fecha_inicio) = ?
           ORDER BY c.localidad, i.fecha_inicio""",
        conn,
        params=(str(anio), f"{mes:02d}"),
    )
    conn.close()

    if df.empty:
        return df, pd.DataFrame()

    resumen = (
        df.groupby(["codigo_central", "localidad"])
        .agg(
            incidencias=("duracion_minutos", "count"),
            downtime_total_min=("duracion_minutos", "sum"),
        )
        .reset_index()
    )
    resumen["downtime_total_min"] = resumen["downtime_total_min"].fillna(0).astype(int)
    resumen["dias"] = resumen["downtime_total_min"] // 1440
    resumen["horas"] = (resumen["downtime_total_min"] % 1440) // 60
    resumen["minutos"] = resumen["downtime_total_min"] % 60
    resumen = resumen.sort_values("downtime_total_min", ascending=False)
    return df, resumen


def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
    return output.getvalue()


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------

st.title("📡 Control de Downtime de Centrales")

menu = st.sidebar.radio(
    "Menú",
    ["Registrar Falla", "Registrar Restablecimiento", "Reporte Mensual", "Centrales Fuera de Servicio"],
)

centrales_df = get_centrales()
opciones_central = {
    f"{row.localidad} ({row.codigo})": row.codigo for row in centrales_df.itertuples()
}

if menu == "Registrar Falla":
    st.header("🔴 Registrar inicio de falla")
    with st.form("form_falla"):
        central_sel = st.selectbox("Central afectada", list(opciones_central.keys()))
        col1, col2 = st.columns(2)
        fecha = col1.date_input("Fecha de la caída", value=datetime.now().date())
        hora = col2.time_input("Hora de la caída", value=datetime.now().time().replace(microsecond=0))
        tecnico = st.text_input("Técnico que reporta")
        observaciones = st.text_area("Observaciones (opcional)")
        submitted = st.form_submit_button("Registrar falla")

        if submitted:
            fecha_inicio = datetime.combine(fecha, hora)
            registrar_falla(opciones_central[central_sel], fecha_inicio, tecnico, observaciones)
            st.success(f"Falla registrada para {central_sel} el {fecha_inicio}.")

elif menu == "Registrar Restablecimiento":
    st.header("🟢 Registrar restablecimiento")
    abiertas = get_incidencias_abiertas()

    if abiertas.empty:
        st.info("No hay centrales fuera de servicio actualmente.")
    else:
        opciones_incid = {
            f"{row.localidad} ({row.codigo_central}) - caída: {row.fecha_inicio}": row.id
            for row in abiertas.itertuples()
        }
        with st.form("form_restablecimiento"):
            incid_sel = st.selectbox("Incidencia a cerrar", list(opciones_incid.keys()))
            col1, col2 = st.columns(2)
            fecha = col1.date_input("Fecha de restablecimiento", value=datetime.now().date())
            hora = col2.time_input("Hora de restablecimiento", value=datetime.now().time().replace(microsecond=0))
            tecnico = st.text_input("Técnico que restablece")
            submitted = st.form_submit_button("Registrar restablecimiento")

            if submitted:
                fecha_fin = datetime.combine(fecha, hora)
                dur = registrar_restablecimiento(opciones_incid[incid_sel], fecha_fin, tecnico)
                st.success(f"Restablecido. Duración de la falla: {dur} minutos ({dur // 60}h {dur % 60}m).")

elif menu == "Centrales Fuera de Servicio":
    st.header("⚠️ Centrales actualmente caídas")
    abiertas = get_incidencias_abiertas()
    if abiertas.empty:
        st.success("Todas las centrales están operativas.")
    else:
        st.dataframe(abiertas, use_container_width=True)

elif menu == "Reporte Mensual":
    st.header("📊 Reporte consolidado mensual")
    col1, col2 = st.columns(2)
    anio = col1.number_input("Año", min_value=2020, max_value=2100, value=datetime.now().year)
    mes = col2.number_input("Mes", min_value=1, max_value=12, value=datetime.now().month)

    detalle, resumen = get_reporte_mensual(int(anio), int(mes))

    if resumen.empty:
        st.info("No hay incidencias registradas para ese mes.")
    else:
        st.subheader("Downtime total por central")
        st.dataframe(
            resumen[["localidad", "codigo_central", "incidencias", "dias", "horas", "minutos", "downtime_total_min"]],
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Descargar resumen (Excel)",
            data=to_excel_bytes(resumen),
            file_name=f"downtime_resumen_{anio}_{mes:02d}.xlsx",
        )

        with st.expander("Ver detalle de todas las incidencias del mes"):
            st.dataframe(detalle, use_container_width=True)
            st.download_button(
                "⬇️ Descargar detalle (Excel)",
                data=to_excel_bytes(detalle),
                file_name=f"downtime_detalle_{anio}_{mes:02d}.xlsx",
            )
