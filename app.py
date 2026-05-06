import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Portal de Citas CEDIS", layout="centered")

st.title("🚚 Registro de Citas para Proveedores")
st.markdown("---")

with st.form("form_citas"):
    no_prov = st.text_input("Número de Proveedor")
    cedis = st.selectbox("Seleccione CEDIS", ["CDMX", "Guadalajara", "Monterrey", "Mérida"])
    fecha = st.date_input("Fecha de entrega", min_value=datetime.today())
    hora = st.selectbox("Horario", ["08:00", "10:00", "12:00", "14:00", "16:00"])
    archivo = st.file_uploader("Subir documentación (PDF)", type=["pdf"])
    
    enviado = st.form_submit_button("Solicitar Cita")
    
    if enviado:
        if no_prov and archivo:
            st.success(f"Solicitud enviada para el proveedor {no_prov}")
            st.balloons()
        else:
            st.error("Por favor llena todos los campos.")
