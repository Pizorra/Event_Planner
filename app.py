import os
from datetime import datetime
import calendar
import base64
from database import Database
from events import Events
from resources import Resources
import streamlit as st

st.set_page_config(
    page_title="Event Planner",
    page_icon="assets/icon.png",
    layout="centered",
)


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


bg_img_base64 = get_base64_of_bin_file("assets/fondo.png")
background_image_style = f"""
    background-image: url("data:image/png;base64,{bg_img_base64}");
    background-attachment: fixed;
    background-size: cover;
"""

st.markdown(
    f"""
    <style>
    /* Fondo principal de la aplicación */
    .stApp {{
        {background_image_style}
    }}
    
    /* Contenedor principal con fondo semitransparente para legibilidad */
    .block-container {{
        background-color: rgba(0, 0, 0, 0.75); /* Fondo OSCURO semitransparente */
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-top: 1rem;
        color: white; /* Texto base blanco */
    }}

    /* Ajuste para el Sidebar */
    [data-testid="stSidebar"] {{
        background-color: rgba(30, 30, 30, 0.9); /* Color oscuro */
        border-right: 1px solid #444;
    }}
    
    /* Títulos y encabezados - FORZAR COLOR BLANCO O CLARO */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #f0f0f0 !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 2px 2px 4px #000000;
    }}

    /* Textos generales y etiquetas */
    p, label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label, .stTimeInput label, .stMultiSelect label {{
        color: #ffffff !important;
        font-weight: 600; /* Un poco mas negrita para que resalte */
    }}

    /* Ajustes para inputs - CAMBIO A TEXTO CLARO GLOBAL */
    input, .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] div, .stDateInput input, .stTimeInput input {{
         color: #ffffff !important; /* Texto blanco */
        caret-color: #ffffff;
    }}
    
    /* Para los valores seleccionados en el Selectbox y Multiselect */
    .stSelectbox div[data-baseweb="select"] span, .stMultiSelect div[data-baseweb="select"] span {{
        color: #ffffff !important;
    }}

    /* Iconos de cerrar en multiselect o flechas */
    .stMultiSelect svg, .stSelectbox svg {{
        fill: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

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
        st.toast("¡Datos guardados correctamente en JSON!", icon="💾")
    else:
        st.toast("Hubo un error al guardar el archivo.", icon="❌")

if st.sidebar.button("📂 Cargar Datos"):
    if DATA.load_from_json("datos_proyecto.json"):
        st.toast("¡Datos cargados exitosamente!", icon="✅")
        st.rerun()
    else:
        st.toast("No se encontró el archivo 'datos_proyecto.json'.", icon="⚠️")

st.sidebar.divider()  # Línea decorativa

with st.sidebar.expander("🛡️ Ver Disponibilidad de Recursos", expanded=False):
    # Generamos la lista de diccionarios para la tabla
    recursos_info = [
        {"Recurso": r.name, "Total": r.quantity} for r in DATA.list_resources()
    ]

    # Mostramos la tabla compacta
    st.dataframe(recursos_info, hide_index=True, use_container_width=True)

### MUSICA ###
with st.sidebar:
    st.divider()
    st.write("🎵 **Ambiente**")
    # Puedes usar un archivo local o una URL directa a un .mp3
    st.audio("assets/8-bit-tavern-355302.mp3", format="audio/mp3", loop=True)

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
            st.session_state["DATA"].load_constraints("constraints_dnd.json")
            st.session_state["confirm_delete"] = False
            st.sidebar.success("Datos borrados. La aplicación fue reiniciada.")
            st.rerun()
    with col2:
        if st.button("❌ Cancelar"):
            st.session_state["confirm_delete"] = False
            st.sidebar.info("Borrado cancelado.")


###  FORMULARIO DE CREACION DE EVENTOS  ###

tab1, tab2 = st.tabs(["Eventos", "Calendario"])

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
    all_options = [r.name for r in DATA.list_resources()]

    # 3. Formulario para el resto de los datos y confirmación
    with st.form("form_event_final"):
        event_name = st.text_input("Nombre del Evento")

        selected_resources = st.multiselect("Selecciona los recursos 🛡️", all_options)

        sugerencia_id = max([e.id for e in DATA.list_events()], default=0) + 1
        event_id = st.number_input(
            "ID del evento", min_value=1, step=1, value=sugerencia_id
        )

        add_event_button = st.form_submit_button("Confirmar Evento")

        if add_event_button:
            # 1. Bandera de validación: Asumimos que todo está bien al principio
            form_is_valid = True

            # --- VALIDACIONES BÁSICAS ---

            # Validación A: Recursos vacíos
            if not selected_resources:
                st.error(
                    "⚠️ Un evento debe tener al menos un recurso asignado.", icon="🛡️"
                )
                form_is_valid = False  # Bajamos la bandera

            # Validación B: Tiempo incoherente
            # Nota: Usamos 'if' separados para poder mostrar TODOS los errores a la vez si hay varios
            if start_time >= end_time:
                st.error(
                    "⚠️ La hora de finalización debe ser posterior a la de inicio.",
                    icon="⏰",
                )
                form_is_valid = False

            # Validación C: ID Duplicado
            # (Fíjate que convertimos a int para comparar peras con peras)
            try:
                id_num = int(event_id)
                if any(e.id == id_num for e in DATA.list_events()):
                    st.error(f"⚠️ Ya existe un evento con el ID {id_num}.", icon="🚫")
                    form_is_valid = False
            except ValueError:
                # Por si acaso el usuario logra meter texto en el number_input (raro, pero posible)
                st.error("⚠️ El ID debe ser un número entero.", icon="🔢")
                form_is_valid = False

            # --- PROCESAMIENTO FINAL ---

            # 2. Solo intentamos guardar si la bandera sigue en pie
            if form_is_valid:

                # Preparar objetos
                resource_objects = [
                    r for r in DATA.list_resources() if r.name in selected_resources
                ]

                # Crear evento
                event = Events(
                    event_name, start_time, end_time, resource_objects, int(event_id)
                )

                # Intentar agregar a la BD (Validación de Constraints complejas)
                ok, msg = DATA.add_event(event, resource_objects)

                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()  # Aquí sí hacemos rerun para limpiar el formulario y actualizar calendarios
                else:
                    # Si falla por lógica de negocio (constraints/cantidad), mostramos el error
                    st.error(f"🚫 **No se pudo agendar:** {msg}", icon="🛑")

                    # Lógica del Detective Temporal (solo si falta cantidad)
                    if "No hay suficientes unidades" in msg:
                        delta_duration = end_time - start_time
                        hours_duration = delta_duration.total_seconds() / 3600

                        suggestion = DATA.find_next_gap(
                            hours_duration, selected_resources, start_time
                        )

                        if suggestion:
                            new_start_date, new_end_date = suggestion
                            st.info(
                                f"💡 **Sugerencia:** Puedes reservar el:\n\n"
                                f"📅 **{new_start_date.strftime('%d/%m/%Y')}** \n"
                                f"⏰ **{new_start_date.strftime('%H:%M')}** - **{new_end_date.strftime('%H:%M')}**",
                                icon="🕵️‍♂️",
                            )
                        else:
                            st.warning("⚠️ No hay huecos disponibles pronto.", icon="⏳")

with tab2:
    st.header("Calendario de Eventos 📅")

    col_cal1, col_cal2 = st.columns(2)
    with col_cal1:
        cal_year = st.number_input(
            "Año", value=datetime.now().year, min_value=2000, max_value=2100
        )
    with col_cal2:
        es_months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        cal_month_name = st.selectbox("Mes", es_months, index=datetime.now().month - 1)
        month_number = es_months.index(cal_month_name) + 1

    cal = calendar.monthcalendar(cal_year, month_number)

    # Encabezados dia
    cols = st.columns(7)
    days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")

    # Rejilla calendario
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    st.markdown(f"##### {day}")
                    # Buscar eventos
                    current_date_start = datetime(cal_year, month_number, day, 0, 0, 0)
                    current_date_obj = current_date_start.date()

                    day_events = []
                    for e in DATA.list_events():
                        start_date = e.start_time.date()
                        end_date = e.end_time.date()

                        if start_date <= current_date_obj <= end_date:
                            # Excluir el día final si el evento termina a las 00:00,
                            # a menos que empiece y termine el mismo día.
                            if (
                                current_date_obj == end_date
                                and e.end_time.hour == 0
                                and e.end_time.minute == 0
                            ):
                                if start_date != end_date:
                                    continue
                            day_events.append(e)

                    colors = [
                        "#FFB3BA",
                        "#FFDFBA",
                        "#FFFFBA",
                        "#BAFFC9",
                        "#BAE1FF",
                        "#E6B3FF",
                        "#F0E68C",
                        "#98FB98",
                        "#AFEEEE",
                        "#D8BFD8",
                    ]

                    for e in day_events:
                        # Extraer los nombres de los recursos

                        resource_names = ", ".join([r.name for r in e.resources])

                        # Seleccionar color basado en el nombre para consistencia
                        color_idx = abs(hash(e.name)) % len(colors)
                        bg_color = colors[color_idx]

                        tooltip_text = (
                            f"ID: {e.id} &#10;"
                            f"Horario: {e.start_time.strftime('%H:%M')} - {e.end_time.strftime('%H:%M')} &#10;"
                            f"Recursos: {resource_names}"
                        )

                        st.markdown(
                            f"""
                            <div style="
                                background-color: {bg_color};
                                color: black;
                                padding: 4px;
                                border-radius: 4px;
                                margin-bottom: 4px;
                                font-size: 12px;
                                border: 1px solid rgba(0,0,0,0.1);
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                cursor : help;
                            " title="{tooltip_text}">
                                {e.name}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    st.divider()  # Una linea separadora bonita
    st.subheader("🗑️ Gestión de Eventos")

    col_del_1, col_del_2 = st.columns([3, 1])

    with col_del_1:
        # Selectbox en vez de number_input para que sea más fácil ver qué se borra
        # Lista de "ID: Nombre del evento"
        options_to_erase = [f"{e.id}: {e.name}" for e in DATA.list_events()]
        event_to_erase = st.selectbox(
            "Selecciona el evento a eliminar:",
            options_to_erase,
            placeholder="Elige uno...",
        )

    with col_del_2:
        st.write("")  # Espacio para alinear el botón abajo
        st.write("")
        if st.button("Eliminar", type="primary"):
            if options_to_erase:
                # Extraemos solo el ID (el numero antes de los dos puntos)
                id_to_delete = int(event_to_erase.split(":")[0])

                if DATA.delete_event(id_to_delete):
                    st.toast(
                        f"Evento {id_to_delete} eliminado correctamente.", icon="🗑️"
                    )
                    st.rerun()
                else:
                    st.error("Error al eliminar.")
            else:
                st.warning("No hay eventos para eliminar.")
