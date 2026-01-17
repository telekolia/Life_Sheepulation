from systems.component_class import Component

class Tile(Component):
    def __init__(self, type, is_passable=True, fertility=0, is_occupied=False):
        self.type = type
        self.is_passable = is_passable
        self.fertillity = fertility
        self.is_occupied = is_occupied