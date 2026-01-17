from systems.component_class import Component
from math import sqrt

class Position(Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def _distance(pos1, pos2):
        return sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)