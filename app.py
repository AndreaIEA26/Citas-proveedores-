import streamlit as st
import psycopg2
import os
from datetime import datetime

# Buscamos la variable en el sistema
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    # Si la variable está vacía, mostramos un error de diagnóstico
    if not DATABASE_URL:
        st.error("⚠️ Error: La variable DATABASE_URL está vacía o no existe en Railway.")
        st.info("Asegúrate de haberle dado al botón 'Deploy' en el panel de Railway después de crear la variable.")
        return
    try:
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
        st.error(f"❌ Error de conexión a la base de datos: {e}")

init_db()

# --- INTERFAZ ---
st.set_page_config(page_title="Portal de Citas | Coppel", layout="wide", page_icon="🚚")
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Coppel.svg/1200px-Coppel.svg.png", width=180)
st.title("Sistema de Gestión de Citas CEDIS")
st.markdown("---")

if DATABASE_URL:
    with st.form("form_citas", clear_on_submit=True):
        st.subheader("📝 Registro de Cita")
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
                        INSERT INTO citas (no_proveedor, razon_social, cedis_origen_num, 
                        cedis_origen_siglas, cedis_destino_num, cedis_destino_siglas, 
                        pedido, sku, descripcion, unidades_facturadas, rampa, 
                        fecha_entrega, hora_entrega, folio_cita) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (no_prov, razon, c_orig_n, c_orig_s, c_dest_n, c_dest_s, 
                          pedido, sku, desc, int(unidades), rampa, fecha, str(hora), folio))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ ¡Cita registrada exitosamente! Folio: **{folio}**")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
