#  Event Planner: D&D Training Center

¡Bienvenido al sistema de gestión para el Centro de Entrenamiento de Aventureros! Esta aplicación está diseñada para coordinar las sesiones de entrenamiento de diversas clases de héroes, asegurando que los recursos (maestros e instalaciones) se utilicen de manera eficiente y siguiendo estrictas reglas de compatibilidad.

##  Dominio Elegido

He elegido el dominio de Gestión de Recursos en un entorno de Fantasía (D&D).

**¿Por qué?**
A diferencia de un calendario común, un centro de entrenamiento de aventureros requiere una lógica de negocio compleja:

1. Los recursos son limitados (solo hay un "Bardo Profesor").
2. Existen dependencias críticas (no puedes usar el Templo sin un Clérigo).
3. Hay conflictos de intereses (los Bárbaros y los Clérigos no se llevan bien en el mismo espacio).

---

## 🛠️ Eventos, Recursos y Restricciones

### 1. Recursos

El sistema maneja dos tipos de recursos:

* **Personales:** Maestros y expertos (ej. *Paladín Maestro, Clérigo Maestro*).
* **Instituciones:** Espacios físicos (ej. *Biblioteca, Campo de Entrenamiento*).

### 2. Restricciones (El "Cerebro" de la App)

El proyecto implementa tres capas de validación lógica:

* **Co-Requisitos (Dependencias):** Ciertos lugares requieren personal específico.
* *Ejemplo:* Para agendar el `Templo`, el sistema te obliga a incluir al `Clérigo Maestro`.


* **Exclusividad Mutual (Conflictos):** Evita que recursos incompatibles coincidan.
* *Ejemplo:* El `Bárbaro Maestro` no puede estar en el mismo evento que la `Biblioteca`.


* **Disponibilidad Temporal (Overbooking):** El sistema calcula en tiempo real si quedan unidades de un recurso para un horario específico, considerando todos los demás eventos ya creados.

---

##  Instalación y Ejecución

Sigue estos pasos para lanzar tu centro de entrenamiento:

1. **Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/nombre-del-repo.git
cd nombre-del-repo

```


2. **Instala las dependencias:**
Asegúrate de tener Python instalado y ejecuta:
```bash
pip install streamlit

```


3. **Lanza la aplicación:**
```bash
streamlit run app.py

```



---

## 🎮 Funcionalidades Clave

* **Gestión Inteligente:** El formulario no permite crear eventos que rompan las reglas de la academia.
* **Calendario Interactivo:** Visualiza tus entrenamientos mensualmente. Pasa el mouse sobre un evento para ver los detalles y recursos asignados.
* **Detective Temporal:** Si intentas crear un evento y no hay recursos, la app te sugerirá automáticamente el próximo hueco libre disponible.
* **Persistencia de Datos:** Guarda y carga tus planes en archivos JSON desde la barra lateral.
* **Interfaz Adaptativa:** Diseño oscuro optimizado con fondos temáticos y acceso rápido al stock de recursos.

---

## 📂 Estructura del Proyecto

* `app.py`: Interfaz de usuario y lógica de Streamlit.
* `database.py`: El motor que gestiona la lógica de eventos y validación de reglas.
* `constraints.py`: Definición de las clases de restricciones.
* `events.py` / `resources.py`: Modelos de objetos del sistema.
* `constraints_dnd.json`: Configuración inicial del mundo.
