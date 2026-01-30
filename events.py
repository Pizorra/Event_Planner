from resources import Resources
from datetime import datetime


class Events:

    def __init__(self, name, start_time: datetime, end_time: datetime, resources, id):

        if start_time > end_time:
            raise ValueError("Valores invalidos de tiempo,pruebe otra vez")

        self.name = name

        self.start_time = start_time

        self.end_time = end_time

        self.resources = resources

        self.id = id

    def duration(self):

        return self.end_time - self.start_time

    def conflicts_with(self, other_event):

        if (
            self.start_time < other_event.end_time
            and self.end_time > other_event.start_time
        ):

            return True

        return False

    def uses_resource(self, resource: Resources):

        for i in self.resources:

            if i == resource:
                return True

        return False

    def __str__(self):
        return f"Evento: {self.name},Inicio: {self.start_time},Fin: {self.end_time},ID: {self.id}"
