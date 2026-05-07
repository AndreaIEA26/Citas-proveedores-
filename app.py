import streamlit as st
import psycopg2
import os
from datetime import datetime

# 1. Configuración de conexión (Base de datos Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Creamos la tabla con todos los campos de tu Excel
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
                unidades_facturadas INTEGER,
                rampa TEXT,
                fecha_entrega DATE,
                hora_entrega TEXT,
                folio_cita TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

if DATABASE_URL:
    init_db()

# --- CONFIGURACIÓN DE INTERFAZ ESTILO COPPEL ---
st.set_page_config(page_title="Portal de Citas | Coppel", layout="wide", page_icon="🚚")

# Encabezado con Logo
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Coppel.svg/1200px-Coppel.svg.png", width=160)
with col_titulo:
    st.title("Sistema de Gestión de Citas CEDIS")
    st.subheader("Registro Oficial de Entregas")

st.markdown("---")

# 2. FORMULARIO DE REGISTRO (Basado en tu tabla de Excel)
with st.form("form_citas", clear_on_submit=True):
    st.info("Complete los campos siguiendo el formato de su reporte de operaciones.")
    
    # Fila 1: Datos Básicos
    c1, c2, c3 = st.columns(3)
    with c1:
        no_prov = st.text_input("No. PROVEEDOR")
    with c2:
        razon = st.text_input("RAZÓN SOCIAL")
    with c3:
        pedido = st.text_input("PEDIDO ($)")

    # Fila 2: Logística de CEDIS
    st.markdown("**📍 Ruta de Transporte**")
    c4, c5, c6, c7 = st.columns(4)
    with c4:
        c_orig_n = st.text_input("NÚMERO CEDIS ORIGEN")
    with c5:
        c_orig_s = st.selectbox("CEDIS ORIGEN", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])
    with c6:
        c_dest_n = st.text_input("NÚMERO CEDIS DESTINO")
    with c7:
        c_dest_s = st.selectbox("CEDIS DESTINO", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])

    # Fila 3: Detalles del Producto
    st.markdown("**📦 Información de Mercancía**")
    c8, c9, c10 = st.columns(3)
    with c8:
        sku = st.text_input("SKU")
    with c9:
        desc = st.text_input("DESCRIPCIÓN")
    with c10:
        unidades = st.number_input("UNIDADES FACTURADAS", min_value=1)

    # Fila 4: Programación (Campos solicitados)
    st.markdown("**⏰ Programación de Cita**")
    c11, c12, c13 = st.columns(3)
    with c11:
        fecha = st.date_input("FECHA DE ENTREGA", min_value=datetime.today())
    with c12:
        # Campo RAMPA solicitado
        rampa = st.text_input("RAMPA ASIGNADA (Si aplica)", placeholder="Ej: 12 o 15")
    with c13:
        # Campo HORA solicitado
        hora = st.time_input("HORA DE CITA")

    st.markdown("<br>", unsafe_allow_html=True)
    enviado = st.form_submit_button("📩 REGISTRAR CITA Y GENERAR FOLIO")

    if enviado:
        if no_prov and razon and sku:
            # Generación automática del FOLIO DE CITA (Ejemplo: GDLJ_04)
            # Usamos las siglas del destino y un número basado en la hora actual
            folio_generado = f"{c_dest_s}_{datetime.now().strftime('%S')}"
            
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO citas (
                        no_proveedor, razon_social, cedis_origen_num, cedis_origen_siglas, 
                        cedis_destino_num, cedis_destino_siglas, pedido, sku, descripcion, 
                        unidades_facturadas, rampa, fecha_entrega, hora_entrega, folio_cita
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (no_prov, razon, c_orig_n, c_orig_s, c_dest_n, c_dest_s, pedido, 
                      sku, desc, unidades, rampa, fecha, str(hora), folio_generado))
                
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"✅ Registro exitoso. **FOLIO DE CITA: {folio_generado}**")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("⚠️ Los campos No. Proveedor, Razón Social y SKU son obligatorios.")
