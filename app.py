import streamlit as st
import psycopg2
import os
from datetime import datetime

# 1. Configuración de conexión (Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
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
        st.error(f"Error de base de datos: {e}")

if DATABASE_URL:
    init_db()

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Portal de Citas | Coppel", layout="wide", page_icon="🚚")

# 2. Encabezado con Identidad Corporativa
# Usamos columnas para poner el nombre/logo a la izquierda
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    # Aquí puedes poner la URL de un logo oficial de Coppel que esté en internet
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Coppel.svg/1200px-Coppel.svg.png", width=150)

with col_titulo:
    st.title("Sistema de Gestión de Citas CEDIS")
    st.subheader("Portal Oficial de Proveedores - Coppel")

st.markdown("---")

# 3. Formulario de entrada
with st.form("form_citas", clear_on_submit=True):
    st.info("Por favor, complete todos los campos requeridos para programar su entrega.")
    
    st.subheader("📋 Datos del Proveedor")
    c1, c2 = st.columns(2)
    with c1:
        no_prov = st.text_input("Número de Proveedor Coppel")
        razon = st.text_input("Razón Social")
    with c2:
        c_orig_n = st.text_input("No. CEDIS Origen")
        c_orig_s = st.selectbox("Origen", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])

    st.markdown("---")
    st.subheader("📦 Detalles de la Mercancía")
    c3, c4, c5 = st.columns(3)
    with c3:
        sku = st.text_input("SKU / Código")
        unidades = st.number_input("Unidades", min_value=1)
    with c4:
        c_dest_n = st.text_input("No. CEDIS Destino")
        c_dest_s = st.selectbox("Destino", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])
    with c5:
        pedido = st.text_input("Folio de Pedido ($)")
        fecha = st.date_input("Fecha de Entrega", min_value=datetime.today())

    desc = st.text_area("Descripción de la Carga")
    hora = st.time_input("Hora Sugerida de Arribo")

    st.markdown("<br>", unsafe_allow_html=True)
    enviado = st.form_submit_button("📩 ENVIAR SOLICITUD A CONTROL DE CITAS")

    if enviado:
        if no_prov and razon and sku:
            folio = f"{c_dest_s}_{no_prov[-2:]}_{datetime.now().strftime('%M%S')}"
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO citas (no_proveedor, razon_social, cedis_origen_num, cedis_origen_siglas, 
                cedis_destino_num, cedis_destino_siglas, pedido, sku, descripcion, unidades, fecha, hora, folio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (no_prov, razon, c_orig_n, c_orig_s, c_dest_n, c_dest_s, pedido, sku, desc, unidades, fecha, str(hora), folio))
            conn.commit()
            cur.close()
            conn.close()
            
            st.success(f"✅ Solicitud recibida con éxito. Su folio de seguimiento es: **{folio}**")
            st.warning("Recuerde que esta cita está sujeta a aprobación por el equipo de Control de Citas.")
        else:
            st.error("⚠️ Error: El Número de Proveedor y el SKU son obligatorios.")
