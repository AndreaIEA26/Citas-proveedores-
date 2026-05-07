import streamlit as st
import psycopg2
import os
from datetime import datetime

# URL PÚBLICA extraída de tu captura de pantalla para conexión garantizada
DATABASE_URL = "postgresql://postgres:bGEZBlLXdyBKTqMMwOUxNDybpNPlCUFz@switchyard.proxy.rlwy.net:20701/railway"

def init_db():
    try:
        # Se usa sslmode='require' porque es una conexión a través de la URL pública
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
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
        st.error(f"Error al inicializar base de datos: {e}")

# Iniciar la base de datos al cargar la app
init_db()

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Portal de Citas | Coppel", layout="wide", page_icon="🚚")

# Estilo visual para mejorar la apariencia
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; height: 3em; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Coppel.svg/1200px-Coppel.svg.png", width=180)
st.title("Sistema de Gestión de Citas CEDIS")
st.markdown("---")

# --- FORMULARIO DE REGISTRO ---
with st.form("form_citas", clear_on_submit=True):
    st.subheader("📝 Datos de la Cita")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        no_prov = st.text_input("No. PROVEEDOR")
        razon = st.text_input("RAZÓN SOCIAL")
    with col2:
        pedido = st.text_input("PEDIDO ($)")
        sku = st.text_input("SKU")
    with col3:
        desc = st.text_input("DESCRIPCIÓN")
        unidades = st.number_input("UNIDADES FACTURADAS", min_value=1, step=1)

    st.markdown("---")
    st.subheader("📍 Logística y Horarios")
    c4, c5, c6, c7 = st.columns(4)
    with c4:
        c_orig_n = st.text_input("NUM. CEDIS ORIGEN")
    with c5:
        c_orig_s = st.selectbox("ORIGEN", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])
    with c6:
        c_dest_n = st.text_input("NUM. CEDIS DESTINO")
    with c7:
        c_dest_s = st.selectbox("DESTINO", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])

    c8, c9, c10 = st.columns(3)
    with c8:
        fecha = st.date_input("FECHA DE ENTREGA", min_value=datetime.today())
    with c9:
        rampa = st.text_input("RAMPA")
    with c10:
        hora = st.time_input("HORA")

    st.markdown("<br>", unsafe_allow_html=True)
    enviado = st.form_submit_button("📩 REGISTRAR CITA EN SISTEMA")

    if enviado:
        if no_prov and razon and sku:
            # Generación de Folio similar a tu Excel (Ej: GDLJ_1245)
            folio_generado = f"{c_dest_s}_{datetime.now().strftime('%M%S')}"
            
            try:
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO citas (
                        no_proveedor, razon_social, cedis_origen_num, cedis_origen_siglas, 
                        cedis_destino_num, cedis_destino_siglas, pedido, sku, descripcion, 
                        unidades_facturadas, rampa, fecha_entrega, hora_entrega, folio_cita
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (no_prov, razon, c_orig_n, c_orig_s, c_dest_n, c_dest_s, pedido, 
                      sku, desc, int(unidades), rampa, fecha, str(hora), folio_generado))
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"✅ ¡Cita procesada con éxito! Su folio es: **{folio_generado}**")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar en la base de datos: {e}")
        else:
            st.warning("⚠️ Por favor rellene los campos obligatorios: Proveedor, Razón Social y SKU.")
