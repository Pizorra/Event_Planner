from database import Database


class Main:

    db = Database

    def add_resources_database(resource):

        Main.db.add_resource(resource)

    def add_event_database(event, resource):

        Main.db.add_event(event, resource)
