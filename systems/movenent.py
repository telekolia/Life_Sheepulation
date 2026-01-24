from random import shuffle
from systems.component_class import Component
from systems.position import Position

class MovementUtils:
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

        if dx != 0 and MovementUtils._can_move_to(pos.x + dx, pos.y, entities, map):
            new_x = pos.x + dx
        elif dy != 0 and MovementUtils._can_move_to(pos.x, pos.y + dy, entities, map):
            new_y = pos.y + dy

        # Обновляем позицию
        if new_x != pos.x or new_y != pos.y:
            entity['Position'].x = new_x
            entity['Position'].y = new_y

            # Тратим энергию на движение
            if 'Hunger' in entity:
                entity['Hunger'].current_satiety -= 0.1

            return True
        return False

    @staticmethod
    def _random_move(entity, entities, map):
        """Случайное блуждание"""
        pos = entity['Position']
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        shuffle(directions)

        for dx, dy in directions:
            (new_x, new_y) = (pos.x + dx, pos.y + dy)

            if MovementUtils._can_move_to(new_x, new_y, entities, map):
                (pos.x, pos.y) = (new_x, new_y)

                # Тратим энергию
                if 'Hunger' in entity:
                    entity['Hunger'].current_satiety -= 0.05
                break

    @staticmethod
    def swap_positions(pos_1, pos_2):
        (x, y) = (pos_1.x, pos_1.y)
        (pos_1.x, pos_1.y) = (pos_2.x, pos_2.y)
        (pos_2.x, pos_2.y) = (x, y)

class MoveComp(Component):
    def __init__(self, state='stop', speed=1, max_pushing_force=1):
        self.state = state
        self.speed = speed
        self.max_pushing_force = max_pushing_force

class MovementSystem:
    def __init__(self, D):
        self.D = D

    def proccess(self):
        for entity in self.D.entities.values():
            if 'MoveComp' not in entity or entity['MoveComp'].state == 'stop':
                continue
            
            if 'Health' in entity and not entity['Health'].is_alive:
                continue
            
            move_comp = entity['MoveComp']
            if move_comp.state == 'path' and 'PathComp' in entity:
                self.path_movement(entity)
            if move_comp.state == 'rand_move':
                self.random_movement(entity)

    def path_movement(self, entity):
        path_comp = entity['PathComp']
        if len(path_comp.path) == 0 or path_comp.target_id == None:
            return

        self.try_move_to(entity, path_comp.pop())


    def random_movement(self, entity):
        """Случайное блуждание"""
        pos = entity['Position']
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        shuffle(directions)

        for dx, dy in directions:
            (new_x, new_y) = (pos.x + dx, pos.y + dy)

            if self.try_move_to(entity, Position(new_x, new_y)):

                # Тратим энергию
                if 'Hunger' in entity:
                    entity['Hunger'].current_satiety -= 0.05
                break

    def try_move_to(self, entity, target_pos):
        map = self.D.map

        if target_pos.x < 0 or target_pos.y < 0 or target_pos.x >= len(map) or target_pos.y >= len(map):
            return False

        if not map[target_pos.x][target_pos.y]['Tile'].is_passable:
            return False

        for other in self.D.entities.values():
            if 'Position' in other and 'Tile' not in other:
                if (other['Position'].x == target_pos.x and other['Position'].y == target_pos.y):
                    return self.try_shtorm_to(entity, other)
                
        pos = entity['Position']
        (pos.x, pos.y) = (target_pos.x, target_pos.y)
        return True

    def try_shtorm_to(self, entity, other):
        pos = entity['Position']
        other_pos = other['Position']

        if 'MoveComp' not in other:
            (pos.x, pos.y) = (other_pos.x, other_pos.y)
            return True
        
        move_comp = entity['MoveComp']
        other_move_comp = other['MoveComp']
        
        if move_comp.max_pushing_force > other_move_comp.max_pushing_force:
            (pos.x, pos.y) = (other_pos.x, other_pos.y)
            return True
        
        return False
        