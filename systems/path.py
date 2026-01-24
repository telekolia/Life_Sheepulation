from systems.component_class import Component
from systems.movenent import MovementUtils
from systems.position import Position
from queue import Queue

class PathComp(Component):
    def __init__(self, target_id=None, path=[]):
        self.target_id = target_id
        self.path = path.copy()

class PathfindingSystem:
    def __init__(self, D):
        self.D = D

    def proccess(self):
        for entity in self.D.entities.values():
            if 'PathComp' in entity and entity['PathComp'].target_id != None:
                self.find_path(entity)

    def find_path(self, entity):
        entity['PathComp'].path.clear()
        pos = entity['Position']
        target_pos = self.D.entities[entity['PathComp'].target_id]

        frontier = Queue()
        frontier.put(pos)
        came_from = dict()
        came_from[pos] = None

        while not frontier.empty():
            current = frontier.get()

            if (current.x, current.y) == (target_pos.x, target_pos.y): 
                break           

            for next in self.get_neighbors(current):
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current

    def get_neighbors(self, pos):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        neighbors = []

        for dx, dy in directions:
            if not MovementUtils._can_move_to(pos.x + dx, pos.y + dy, self.D.entities, self.D.map):
                next
            neighbors.append(Position(pos.x + dx, pos.y + dy))
        
        return neighbors   