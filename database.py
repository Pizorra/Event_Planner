from resources import Resources
from events import Events
from datetime import datetime
import json


class Database:

    def __init__(self, resources: list, events: list):

        self.resources = resources
        self.events = events

    def add_event(self, event: Events, resource: list):

        for i in self.events:

            if event.conflicts_with(i):
                return "Conflicto detectado,no se puede agregar"

        for resource_item in resource:
            if not resource_item.is_available():
                return "Recurso no disponible"

        for resource_item in resource:
            resource_item.quantity -= 1

        self.events.append(event)

    def add_resource(self, resource: Resources):

        self.resources.append(resource)

    def list_events(self):

        return self.events

    def list_resources(self):
        return self.resources

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
                    "resources": e.resources,
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

                new_event = Events(
                    e_data["name"], start, end, e_data["resources"], e_data["id"]
                )

                self.events.append(new_event)

            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error al cargar: {e}")
            return False
