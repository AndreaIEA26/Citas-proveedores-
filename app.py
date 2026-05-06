import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Portal de Citas CEDIS", layout="wide")

st.title("🚚 Registro de Citas para Entregas")
st.markdown("---")

# Usamos columnas para que no sea una lista infinita hacia abajo
with st.form("form_citas"):
    st.subheader("Datos del Proveedor y Origen")
    col1, col2 = st.columns(2)
    with col1:
        no_proveedor = st.text_input("No. Proveedor (Ej. 79774)")
        razon_social = st.text_input("Razón Social")
    with col2:
        num_cedis_origen = st.text_input("Número de CEDIS Origen")
        cedis_origen = st.selectbox("CEDIS Origen (Siglas)", ["GDLJ", "CDMX", "MTY", "MER"])

    st.markdown("---")
    st.subheader("Datos de la Entrega (Destino)")
    col3, col4 = st.columns(2)
    with col3:
        num_cedis_destino = st.text_input("Número de CEDIS Destino")
        cedis_destino = st.selectbox("CEDIS Destino", ["GDLJ", "CDMX", "MTY", "MER"])
    with col4:
        fecha = st.date_input("Fecha de entrega", min_value=datetime.today())
        hora = st.time_input("Hora sugerida")

    st.markdown("---")
    st.subheader("Detalles del Pedido")
    col5, col6, col7 = st.columns(3)
    with col5:
        pedido = st.text_input("Pedido ($)")
    with col6:
        sku = st.text_input("SKU / Código de Producto")
    with col7:
        unidades = st.number_input("Unidades Facturadas", min_value=1)

    descripcion = st.text_area("Descripción del Producto")
    archivo = st.file_uploader("Subir documentación soporte (PDF)", type=["pdf"])
    
    st.markdown("---")
    enviado = st.form_submit_button("🚀 Solicitar Cita y Generar Folio")
    
    if enviado:
        if no_proveedor and razon_social and sku:
            # Simulación de generación de folio como en tu tabla (GDLJ_01)
            folio = f"{cedis_destino}_{no_proveedor[-2:]}" 
            st.success(f"✅ ¡Solicitud Enviada! Tu Folio de Cita es: **{folio}**")
            st.info("El equipo de control de citas revisará la información y te notificará por correo.")
        else:
            st.error("⚠️ Por favor llena los campos obligatorios (No. Proveedor, Razón Social y SKU).")
