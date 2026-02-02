from resources import Resources
from events import Events
from datetime import datetime
from constraints import CoRequisite, MutualExclusion, TypeExclusion
from datetime import timedelta
import json

### Constructor ###


class Database:

    def __init__(self, resources: list, events: list):

        self.resources = resources
        self.events = events
        self.constraints = []

    ### Logica para Eventos ###

    def add_event(self, event: Events, resource_list: list):

        is_valid, message = self.validate_constraints(resource_list)
        if not is_valid:
            return (False, message)

        for res in resource_list:
            available = self.get_available_resource_quantity(
                res.name, event.start_time, event.end_time
            )

            if available < 1:
                return (
                    False,
                    f"No hay suficientes unidades de {res.name} para este horario",
                )

        self.events.append(event)
        return (True, "Evento agregado correctamente")

    def delete_event(self, event_id):

        for event in self.events:
            if event.id == event_id:

                self.events.pop(self.events.index(event))

                return True

        print("El id no existe")
        return False

    def list_events(self):

        return self.events

    def find_event_by_id(self, event_id):

        for event in self.events:

            if event.id == event_id:
                return event
        return None

    ### Logica para Recursos ###

    def resource_usage(self, resource_name):
        res = []

        for event in self.events:

            for resource in event.resources:

                if resource.name == resource_name:
                    res.append(event.name)
        return res

    def get_available_resource_quantity(self, resource_name, start_time, end_time):

        resource = next((r for r in self.resources if r.name == resource_name), None)

        if not resource:
            return 0

        available = resource.quantity

        temp_event = Events("Temp", start_time, end_time, [], 0)

        for event in self.events:

            if event.conflicts_with(temp_event) and event.uses_resource(resource):
                available -= 1

        return available

    def add_resource(self, resource: Resources):

        self.resources.append(resource)

    def list_resources(self):
        return self.resources

    ### Logica para Restriciones ###

    def add_constraint(self, constraint):
        """Agrega una restricción a la lista"""
        self.constraints.append(constraint)

    def validate_constraints(self, resources):
        """Valida que los recursos cumplan todas las restriciones.
        Retorna: (True,message) si es válido, o (False,error_message) si viola algo
        """

        resource_names = [r.name for r in resources]
        resources_type = [r.type for r in resources]

        for constraint in self.constraints:

            # Tipo 1: Co-Requisito
            if isinstance(constraint, CoRequisite):
                # Si uso esto,DEBO usar esto otro
                if constraint.when_using_this in resource_names:
                    if constraint.requires_this not in resource_names:
                        return (
                            False,
                            f"Error: {constraint.when_using_this} requiere {constraint.requires_this}",
                        )

            if isinstance(constraint, MutualExclusion):
                # No puedo tener ambos recursos a la vez
                if (
                    constraint.resource_a in resource_names
                    and constraint.resource_b in resource_names
                ):
                    return (
                        False,
                        f"Error: {constraint.resource_a} y {constraint.resource_b} no pueden estar juntos",
                    )

            if isinstance(constraint, TypeExclusion):
                # No puede haber dos recursos del mismo tipo
                type_counts = {}

                for rtype in resources_type:

                    type_counts[rtype] = type_counts.get(rtype, 0) + 1

                for rtype, count in type_counts.items():
                    if count > 1:
                        return (
                            False,
                            f"Error: No puede haber multiples recursos de tipo '{rtype}'",
                        )
        return (True, "Restricciones válidas")

    def load_constraints(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)

            for res_data in data.get("resources", []):
                res = Resources(
                    res_data["name"], res_data["type"], res_data["quantity"]
                )
                self.add_resource(res)

            # Co-requisites: por cada recurso requerido, agregar restricciones
            for required_resource, using_resources in data.get(
                "co_requisites", {}
            ).items():

                for using_resource in using_resources:

                    c = CoRequisite(required_resource, using_resource)
                    self.add_constraint(c)

            # Mutual exclusions
            for res_a, res_b in data.get("mutual_exclusions", []):
                c = MutualExclusion(res_a, res_b)
                self.add_constraint(c)

            # Type Exclusion:booleano
            if data.get("type_exclusion", False):
                c = TypeExclusion()
                self.add_constraint(c)

            return True

        except Exception as e:

            print(f"Error loading constraints: {e}")
            return False

    ### Busqueda automatica de espacios entre eventos ###

    def find_next_gap(self, duration_hours, resource_names, start_search_dt=None):
        if start_search_dt is None:
            start_search_dt = datetime.now()

        target_resources = [
            r for r in self.list_resources() if r.name in resource_names
        ]

        relevant_events = [
            ev
            for ev in self.events
            if any(
                res.name in [r.name for r in ev.resources] for res in target_resources
            )
        ]

        relevant_events.sort(key=lambda x: x.start_time)

        current_start = start_search_dt

        # Bucle de Busqueda(Max 7 dias)

        limit_date = start_search_dt + timedelta(days=7)

        while current_start + timedelta(hours=duration_hours) <= limit_date:
            current_end = current_start + timedelta(hours=duration_hours)

            conflict = None

            for ev in relevant_events:

                # Comprobar el posible evento con el actual y chequear overlaps

                if self.check_overlap(
                    current_start, current_end, ev.start_time, ev.end_time
                ):

                    # Si hay overlap chequeamos igual que queden recursos libres y que se cumplan los constraints

                    if not self.is_legally_available(
                        current_start, current_end, target_resources
                    ):
                        conflict = ev
                        break

            if conflict is None:
                # No conflictos se encontro el gap
                return current_start, current_end

            else:
                # Salto
                current_start = conflict.end_time

        return None

    ### Funciones Auxiliares de Find_Gap ###

    def check_overlap(self, start1, end1, start2, end2):
        # Verifica si dos intervalos de tiempo se cruzan
        return start1 < end2 and start2 < end1

    def is_legally_available(self, start_time, end_time, resource_list):
        # Verifica disponibilidad fisica y cumplimiento de restricciones.

        for res in resource_list:
            qty = self.get_available_resource_quantity(res.name, start_time, end_time)
            if qty <= 0:
                return False

        is_valid, message = self.validate_constraints(resource_list)
        return is_valid

    ### Persistencia de Datos ###

    def save_to_json(self, filename):

        data_to_save = {"resources": [], "events": []}

        for r in self.resources:
            data_to_save["resources"].append(
                {"name": r.name, "type": r.type, "quantity": r.quantity}
            )

        for e in self.events:
            data_to_save["events"].append(
                {
                    "name": e.name,
                    "start_time": e.start_time.isoformat(),
                    "end_time": e.end_time.isoformat(),
                    "resources": [r.name for r in e.resources],
                    "id": e.id,
                }
            )
        try:
            with open(filename, "w") as file:
                json.dump(data_to_save, file, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False

    def load_from_json(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)

            self.resources = []
            self.events = []

            for r_data in data["resources"]:

                new_resource = Resources(
                    r_data["name"], r_data["type"], r_data["quantity"]
                )

                self.resources.append(new_resource)

            for e_data in data["events"]:

                start = datetime.fromisoformat(e_data["start_time"])
                end = datetime.fromisoformat(e_data["end_time"])

                resource_objs = []
                for rname in e_data["resources"]:

                    for res in self.resources:

                        if res.name == rname:

                            resource_objs.append(res)
                            break

                new_event = Events(
                    e_data["name"], start, end, resource_objs, e_data["id"]
                )

                self.events.append(new_event)

            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error al cargar: {e}")
            return False
