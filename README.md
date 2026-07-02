# Control de Downtime de Centrales — MVP

Sistema para registrar caídas y restablecimientos de centrales telefónicas,
y generar el reporte consolidado de downtime mensual.

## Requisitos
- Python 3.9+

## Instalación local

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar la base de datos (crea downtime.db y carga las 61 centrales)
python init_db.py

# 4. Ejecutar la aplicación
streamlit run app.py
```

Streamlit abrirá automáticamente el navegador en `http://localhost:8501`.

## Uso

1. **Registrar Falla**: el técnico selecciona la central, confirma fecha/hora
   (auto-sugerida como "ahora") y registra observaciones. La central queda
   marcada como "Fuera de Servicio".
2. **Registrar Restablecimiento**: se listan solo las centrales actualmente
   caídas; al elegir una y confirmar la hora, el sistema calcula
   automáticamente la duración de la falla en minutos.
3. **Centrales Fuera de Servicio**: vista rápida de todo lo que está caído
   en este momento (útil como pizarra de NOC).
4. **Reporte Mensual**: selecciona año/mes y obtiene el downtime total
   acumulado por central (días/horas/minutos), con exportación a Excel
   tanto del resumen como del detalle de incidencias.

## Estructura

```
telecom_downtime/
├── app.py            # Aplicación Streamlit (UI + lógica)
├── init_db.py         # Script de inicialización y carga del catálogo de centrales
├── schema.sql         # Definición de tablas (centrales, incidencias)
├── requirements.txt
└── downtime.db        # Se genera al ejecutar init_db.py (SQLite)
```

## Notas sobre despliegue (siguiente paso)

- Para producción, evita depender solo del archivo `downtime.db` local: usa
  un volumen persistente, o migra la conexión a una base Postgres gratuita
  (por ejemplo Neon.tech o Supabase) cambiando solo la capa de conexión en
  `app.py` (de `sqlite3` a `psycopg2`/`SQLAlchemy`).
- Deploy recomendado: subir este repo a GitHub y conectarlo a
  [Streamlit Community Cloud](https://streamlit.io/cloud) (gratis) o a
  [Render](https://render.com) como Web Service.
- Configura backups automáticos diarios de la base de datos (export a
  Excel/CSV a un Google Drive o bucket S3) mientras migras a Postgres.

## Próximos pasos sugeridos

- Autenticación simple por técnico (usuario/contraseña o PIN).
- Notificaciones automáticas (correo/WhatsApp API) cuando una central lleva
  más de X horas caída.
- Migración a PostgreSQL + despliegue en Render/Railway cuando el número de
  técnicos concurrentes crezca.
