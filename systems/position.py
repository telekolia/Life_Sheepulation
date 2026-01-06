from systems.component_class import Component
from math import sqrt
import random

class Position(Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def _distance(pos1, pos2):
        return sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)

    @staticmethod
    def _can_move_to(x, y, map, entities):
        if x < 0 or y < 0 or x >= len(map) or y >= len(map[0]):
            return False

        if not map[x][y].passable:
            return False

        for other in entities:
            if 'Position' in other:
                if (other['Position'].x == x and other['Position'].y == y and 'Plant' not in other):
                    return False

        return True

    @staticmethod
    def _move_towards(entity, entities, target_pos, map):
        pos = entity['Position']
        # Вычисляем направление
        dx = 0
        dy = 0

        if pos.x < target_pos.x:
            dx = 1
        elif pos.x > target_pos.x:
            dx = -1

        if pos.y < target_pos.y:
            dy = 1
        elif pos.y > target_pos.y:
            dy = -1

        # Чтобы глазки не болели не двигаемся по диагонали
        new_x = pos.x
        new_y = pos.y

        if dx != 0 and Position._can_move_to(pos.x + dx, pos.y, map, entities):
            new_x = pos.x + dx
        elif dy != 0 and Position._can_move_to(pos.x, pos.y + dy, map, entities):
            new_y = pos.y + dy

        # Обновляем позицию
        if new_x != pos.x or new_y != pos.y:
            entity['Position'].x = new_x
            entity['Position'].y = new_y

            # Тратим энергию на движение
            if 'Hunger' in entity:
                entity['Hunger'].current_satiety -= 0.1

    @staticmethod
    def _random_move(entity, map, entities):
        """Случайное блуждание"""
        pos = entity['Position']
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)

        for dx, dy in directions:
            (new_x, new_y) = (pos.x + dx, pos.y + dy)

            if Position._can_move_to(new_x, new_y, map, entities):
                (pos.x, pos.y) = (new_x, new_y)

                # Тратим энергию
                if 'Hunger' in entity:
                    entity['Hunger'].current_satiety -= 0.05
                break
