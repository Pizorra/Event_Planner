import os
from datetime import datetime
from database import Database
from events import Events
from resources import Resources
import streamlit as st

if "DATA" not in st.session_state:
    st.session_state["DATA"] = Database([], [])

DATA = st.session_state["DATA"]

st.title("Planificador de Eventos")

st.sidebar.header("Opciones")

if st.sidebar.button("💾 Guardar Cambios"):
    if DATA.save_to_json("datos_proyecto.json"):
        st.sidebar.success("Datos guardados correctamente!")
    else:
        st.sidebar.error("Hubo un error al guardar")

if st.sidebar.button("📂 Cargar Datos"):
    if DATA.load_from_json("datos_proyecto.json"):
        st.sidebar.success("Datos cargados exitosamente!")
        st.rerun()
    else:
        st.sidebar.error("No se encontro el archivo o hubo un error")

col1, col2 = st.sidebar.columns(2)

with col1:

    if st.button("🗑️ Borrar Datos"):
        st.session_state["confirm_delete"] = True

if st.session_state.get("confirm_delete", False):
    st.sidebar.warning("¿Estás seguro de que deseas borrar todos los datos?")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("✅ Sí, borrar"):
            if os.path.exists("datos_proyecto.json"):
                os.remove("datos_proyecto.json")
            st.session_state["DATA"] = Database([], [])
            st.session_state["confirm_delete"] = False
            st.sidebar.success("Datos borrados. La aplicación fue reiniciada.")
            st.rerun()
    with col2:
        if st.button("❌ Cancelar"):
            st.session_state["confirm_delete"] = False
            st.sidebar.info("Borrado cancelado.")

tab1, tab2 = st.tabs(["Recursos", "Eventos"])

with tab1:
    with st.form("form_resource"):

        st.header("Gestion de Recursos")

        resource_name = st.text_input("Nombre del recurso")

        resource_type = st.text_input("Tipo de recurso")

        resource_quantity = st.number_input("Cantidad del recurso", min_value=1)

        add_resource_button = st.form_submit_button("Agregar Recurso")

if add_resource_button:
    resource = Resources(resource_name, resource_type, resource_quantity)
    DATA.add_resource(resource)
    st.success(f"Recurso {resource_name} agregado exitosamente")

resources_table = []
for r in DATA.list_resources():
    resources_table.append({"Nombre": r.name, "Tipo": r.type, "Cantidad": r.quantity})
st.table(resources_table)

with tab2:
    with st.form("form_event"):

        st.header("Gestion de Eventos")
        event_name = st.text_input("Nombre del Evento")

        start_date = st.date_input("Fecha de Inicio")
        start_hour = st.time_input("Hora de inicio")

        end_date = st.date_input("Fecha de Fin")
        end_hour = st.time_input("Hora de Fin")

        selected_resources = st.multiselect(
            "Recursos Necesarios", [r.name for r in DATA.list_resources()]
        )
        for r in DATA.list_resources():
            if r.name in selected_resources:
                resource_objects = [
                    r for r in DATA.list_resources() if r.name in selected_resources
                ]

        event_id = st.number_input("ID del evento", min_value=1)

        start_time = datetime.combine(start_date, start_hour)
        end_time = datetime.combine(end_date, end_hour)

        add_event_button = st.form_submit_button("Confirmar Evento")

if add_event_button:

    event = Events(event_name, start_time, end_time, selected_resources, event_id)
    DATA.add_event(event, resource_objects)
    st.success(f"Evento {event_name} agregado correctamente")

st.table(
    [
        {
            "Nombre": e.name,
            "Inicio": e.start_time,
            "Fin": e.end_time,
            "Recursos": [r for r in e.resources],
            "Id": e.id,
        }
        for e in DATA.list_events()
    ]
)
