import streamlit as st
import psycopg2
import os
from datetime import datetime

# 1. Configuración de conexión a la base de datos
# Railway asigna automáticamente la variable DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    """Crea la tabla en la base de datos si no existe"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id SERIAL PRIMARY KEY,
                no_proveedor TEXT,
                razon_social TEXT,
                cedis_origen_num TEXT,
                cedis_origen_siglas TEXT,
                cedis_destino_num TEXT,
                cedis_destino_siglas TEXT,
                pedido TEXT,
                sku TEXT,
                descripcion TEXT,
                unidades INTEGER,
                fecha DATE,
                hora TEXT,
                folio TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estatus TEXT DEFAULT 'Pendiente'
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

# Ejecutar la creación de la tabla al arrancar
if DATABASE_URL:
    init_db()
else:
    st.warning("⚠️ No se detectó la base de datos. Verifica que PostgreSQL esté agregado en Railway.")

# 2. Configuración de la interfaz
st.set_page_config(page_title="Portal de Citas CEDIS", layout="wide")

st.title("🚚 Registro Oficial de Citas - Control de Entregas")
st.markdown("---")

# 3. Formulario de entrada de datos
with st.form("form_citas", clear_on_submit=True):
    st.subheader("Información del Proveedor y Origen")
    col1, col2 = st.columns(2)
    with col1:
        no_prov = st.text_input("No. Proveedor (Ej: 79774)")
        razon = st.text_input("Razón Social")
    with col2:
        c_orig_n = st.text_input("Número de CEDIS Origen")
        c_orig_s = st.selectbox("Siglas CEDIS Origen", ["GDLJ", "CDMX", "MTY", "MER"])

    st.markdown("---")
    st.subheader("Detalles del Destino y Mercancía")
    col3, col4 = st.columns(2)
    with col3:
        c_dest_n = st.text_input("Número de CEDIS Destino")
        c_dest_s = st.selectbox("Siglas CEDIS Destino", ["GDLJ", "CDMX", "MTY", "MER"])
        pedido = st.text_input("Pedido ($)")
    with col4:
        sku = st.text_input("SKU")
        unidades = st.number_input("Unidades Facturadas", min_value=1, step=1)
        desc = st.text_area("Descripción del Producto")

    st.markdown("---")
    st.subheader("Programación")
    col5, col6 = st.columns(2)
    with col5:
        fecha = st.date_input("Fecha de entrega", min_value=datetime.today())
    with col6:
        hora = st.time_input("Hora sugerida")

    enviado = st.form_submit_button("✅ Guardar Registro y Generar Folio")

    if enviado:
        if no_prov and razon and sku:
            try:
                # Generación de Folio (Siglas Destino + Proveedor + Minuto/Segundo para que sea único)
                folio = f"{c_dest_s}_{no_prov[-2:]}_{datetime.now().strftime('%M%S')}"
                
                # Insertar en la base de datos
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO citas (
                        no_proveedor, razon_social, cedis_origen_num, cedis_origen_siglas, 
                        cedis_destino_num, cedis_destino_siglas, pedido, sku, descripcion, 
                        unidades, fecha, hora, folio
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (no_prov, razon, c_orig_n, c_orig_s, c_dest_n, c_dest_s, pedido, sku, desc, unidades, fecha, str(hora), folio))
                
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"¡Registro exitoso! Tu Folio de Cita es: **{folio}**")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar los datos: {e}")
        else:
            st.error("⚠️ Por favor llena los campos obligatorios: No. Proveedor, Razón Social y SKU.")
