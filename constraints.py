class Constraint:
    """Clase base para todas las restricciones"""
    pass


class CoRequisite(Constraint):
    """Recurso A requiere Recurso B presente en el evento"""
    def __init__(self, requires_this, when_using_this):
        self.requires_this = requires_this          # nombre del recurso requerido
        self.when_using_this = when_using_this      # nombre del recurso que lo requiere

    def __repr__(self):
        return f"CoRequisite: {self.when_using_this} requires {self.requires_this}"


class MutualExclusion(Constraint):
    """Recurso A y B no pueden estar en el mismo evento"""
    def __init__(self, resource_a, resource_b):
        self.resource_a = resource_a
        self.resource_b = resource_b

    def __repr__(self):
        return f"MutualExclusion: {self.resource_a} and {self.resource_b} cannot coexist"


class TypeExclusion(Constraint):
    """No puede haber múltiples recursos del mismo tipo en un evento"""
    def __init__(self):
        pass

    def __repr__(self):
        return "TypeExclusion: No multiple resources of same type"
