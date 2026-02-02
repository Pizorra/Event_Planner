import os
from datetime import datetime
from database import Database
from events import Events
from resources import Resources
import streamlit as st

### CARGAR ESTADO DEL JSON ###

if "DATA" not in st.session_state:
    st.session_state["DATA"] = Database([], [])
    st.session_state["DATA"].load_constraints("constraints_dnd.json")

DATA = st.session_state["DATA"]

st.title("Planificador de Eventos")

### CARGAR O GUARDAR CAMBIOS BOTONES ###

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


### BORRAR DATOS DEL JSON ###

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

### LISTA DE RECURSOS DISPONIBLES ###

st.subheader("Recursos Disponibles")
resources_table = []
for r in DATA.list_resources():
    resources_table.append({"Nombre": r.name, "Tipo": r.type, "Cantidad": r.quantity})
st.table(resources_table)

###  FORMULARIO DE CREACION DE EVENTOS  ###

(tab1,) = st.tabs(["Eventos"])

with tab1:

    st.header("Gestión de Eventos")

    # 1. Inputs fuera del formulario para permitir reactividad dinámica
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de Inicio")
        start_hour = st.time_input("Hora de inicio")
    with col2:
        end_date = st.date_input("Fecha de Fin")
        end_hour = st.time_input("Hora de Fin")

    start_time = datetime.combine(start_date, start_hour)
    end_time = datetime.combine(end_date, end_hour)

    # 2. Filtrado dinámico (se ejecuta cada vez que cambia el tiempo)
    available_options = [
        r.name
        for r in DATA.list_resources()
        if DATA.get_available_resource_quantity(r.name, start_time, end_time) > 0
    ]

    # 3. Formulario para el resto de los datos y confirmación
    with st.form("form_event_final"):
        event_name = st.text_input("Nombre del Evento")

        selected_resources = st.multiselect(
            "Recursos Disponibles en este horario 🟢", available_options
        )

        event_id = st.number_input("ID del evento", min_value=1)

        add_event_button = st.form_submit_button("Confirmar Evento")

        if add_event_button:
            # Obtenemos los objetos reales de los nombres seleccionados
            resource_objects = [
                r for r in DATA.list_resources() if r.name in selected_resources
            ]

            event = Events(event_name, start_time, end_time, resource_objects, event_id)
            ok, msg = DATA.add_event(event, resource_objects)

            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(f"No se pudo crear el evento: {msg}")

                # Calculo de sugerencia
                delta_duration = end_time - start_time
                hours_duration = delta_duration.total_seconds() / 3600

                suggestion = DATA.find_next_gap(
                    hours_duration, selected_resources, start_time
                )

                if suggestion:
                    new_start_date, new_end_date = suggestion
                    st.info(
                        f"💡 **Sugerencia:** El próximo hueco disponible para estos recursos es el:"
                    )
                    st.code(
                        f"{new_start_date.strftime('%d/%m/%Y de %H:%M')} a {new_end_date.strftime('%H:%M')}"
                    )
                else:
                    st.warning(
                        "⚠️ No se encontraron huecos disponibles en los próximos 7 días."
                    )

### LISTA DE EVENTOS ###

st.table(
    [
        {
            "Nombre": e.name,
            "Inicio": e.start_time,
            "Fin": e.end_time,
            "Recursos": ",".join(r.name for r in e.resources),
            "Id": e.id,
        }
        for e in DATA.list_events()
    ]
)
### BOTON ELIMINAR EVENTO ###
st.subheader("Eliminar Evento")
event_to_delete = st.number_input("ID del evento a eliminar", min_value=1)
if st.button("🗑️ Eliminar Evento"):
    if DATA.delete_event(event_to_delete):
        st.success("Evento eliminado!")
        st.rerun()
    else:
        st.error("Evento no encontrado")
