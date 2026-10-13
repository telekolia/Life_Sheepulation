from systems.component_class import Component
from systems.movenent import MovementUtils
from systems.position import Position
from queue import Queue


class PathComp(Component):
    def __init__(self):
        self.destination = None
        self.path = []

    def clear(self):
        self.destination = None
        self.path.clear()

    def clone(self, **kwargs):
        cloned = super().clone(**kwargs)
        if cloned.destination is not None:
            pos = cloned.destination
            cloned.destination = Position(pos.x, pos.y)
        return cloned


class PathfindingSystem:
    def __init__(self, D):
        self.D = D

    def proccess(self):
        for entity in self.D.entities.values():
            if 'PathComp' in entity and entity['PathComp'].destination is not None:
                if 'Health' in entity and not entity['Health'].is_alive:
                    continue
                self.find_path(entity, entity['PathComp'].destination)

    def find_path(self, entity, destination, max_distanse=10, arrival_distance=0):
        """Return success, including an already reached destination.

        Coordinates are copied; PathComp.destination is the actual end cell.
        None as max_distanse allows searching the whole finite map.
        """
        target_pos = Position(destination.x, destination.y)
        path_comp = entity['PathComp']
        path_comp.clear()
        pos = entity['Position']
        start = Position(pos.x, pos.y)
        frontier = Queue()
        frontier.put(start)
        came_from = {start: None}
        reached = None

        while not frontier.empty():
            current = frontier.get()
            if max_distanse is not None and Position._distance(start, current) > max_distanse:
                continue
            if Position._distance(current, target_pos) <= arrival_distance:
                reached = current
                break
            for next_pos in self.get_neighbors(current):
                if next_pos not in came_from:
                    frontier.put(next_pos)
                    came_from[next_pos] = current

        if reached is None:
            return False

        path_comp.destination = Position(reached.x, reached.y)
        current = reached
        while current != start:
            path_comp.path.append(current)
            current = came_from[current]
        path_comp.path.reverse()
        return True

    def reachable_positions(self, entity, max_distanse):
        """Reachable cells inside the radius, excluding the start; no mutation."""
        pos = entity['Position']
        start = Position(pos.x, pos.y)
        frontier = Queue()
        frontier.put(start)
        visited = {start}
        reachable = []
        while not frontier.empty():
            current = frontier.get()
            for next_pos in self.get_neighbors(current):
                if (next_pos in visited
                    or Position._distance(start, next_pos) > max_distanse):
                    continue
                visited.add(next_pos)
                reachable.append(next_pos)
                frontier.put(next_pos)
        return reachable

    def get_neighbors(self, pos):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        neighbors = []
        for dx, dy in directions:
            x, y = pos.x + dx, pos.y + dy
            if MovementUtils._can_move_to(x, y, self.D.entities, self.D.map):
                neighbors.append(Position(x, y))
        return neighbors
