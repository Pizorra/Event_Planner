class Resources:

    def __init__(self, name, type, quantity):

        self.name = name
        self.type = type
        self.quantity = quantity

    def is_available(self):
        if self.quantity > 0:
            return True
        return False
