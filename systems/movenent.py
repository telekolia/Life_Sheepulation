import random

class Movement:
    @staticmethod
    def _can_move_to(x, y, entities, map):
        if x < 0 or y < 0 or x >= len(map) or y >= len(map):
            return False

        if not map[x][y]['Tile'].is_passable:
            return False

        for other in entities.values():
            if 'Position' in other and 'Tile' not in other:
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

        if dx != 0 and Movement._can_move_to(pos.x + dx, pos.y, entities, map):
            new_x = pos.x + dx
        elif dy != 0 and Movement._can_move_to(pos.x, pos.y + dy, entities, map):
            new_y = pos.y + dy

        # Обновляем позицию
        if new_x != pos.x or new_y != pos.y:
            entity['Position'].x = new_x
            entity['Position'].y = new_y

            # Тратим энергию на движение
            if 'Hunger' in entity:
                entity['Hunger'].current_satiety -= 0.1

    @staticmethod
    def _random_move(entity, entities, map):
        """Случайное блуждание"""
        pos = entity['Position']
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)

        for dx, dy in directions:
            (new_x, new_y) = (pos.x + dx, pos.y + dy)

            if Movement._can_move_to(new_x, new_y, entities, map):
                (pos.x, pos.y) = (new_x, new_y)

                # Тратим энергию
                if 'Hunger' in entity:
                    entity['Hunger'].current_satiety -= 0.05
                break