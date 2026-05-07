import streamlit as st
import psycopg2
import os
from datetime import datetime

# El código tomará automáticamente la URL que acabas de actualizar en Railway
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    if not DATABASE_URL:
        st.error("Error: No se encontró la variable DATABASE_URL en Railway.")
        return
    try:
        # Importante: sslmode='require' para conexiones externas
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
        st.error(f"Error de conexión: {e}")

init_db()

# --- INTERFAZ DEL PORTAL ---
st.set_page_config(page_title="Portal de Citas | Coppel", layout="wide", page_icon="🚚")
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Coppel.svg/1200px-Coppel.svg.png", width=180)
st.title("Sistema de Gestión de Citas CEDIS")
st.markdown("---")

with st.form("form_citas", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        no_prov = st.text_input("No. PROVEEDOR")
        razon = st.text_input("RAZÓN SOCIAL")
    with col2:
        pedido = st.text_input("PEDIDO ($)")
        sku = st.text_input("SKU")
    with col3:
        desc = st.text_input("DESCRIPCIÓN")
        unidades = st.number_input("UNIDADES FACTURADAS", min_value=1)

    st.markdown("---")
    st.subheader("📍 Logística")
    c4, c5, c6, c7 = st.columns(4)
    with c4: c_orig_n = st.text_input("NUM. CEDIS ORIGEN")
    with c5: c_orig_s = st.selectbox("ORIGEN", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])
    with c6: c_dest_n = st.text_input("NUM. CEDIS DESTINO")
    with c7: c_dest_s = st.selectbox("DESTINO", ["GDLJ", "CDMX", "MTY", "CUL", "MER"])

    c8, c9, c10 = st.columns(3)
    with c8: fecha = st.date_input("FECHA DE ENTREGA")
    with c9: rampa = st.text_input("RAMPA")
    with c10: hora = st.time_input("HORA")

    enviado = st.form_submit_button("📩 REGISTRAR CITA")

    if enviado:
        if no_prov and sku:
            folio = f"{c_dest_s}_{datetime.now().strftime('%M%S')}"
            try:
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO citas (no_proveedor, razon_social, sku, folio_cita) 
                    VALUES (%s, %s, %s, %s)
                """, (no_prov, razon, sku, folio))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"✅ Cita registrada. Folio: {folio}")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
