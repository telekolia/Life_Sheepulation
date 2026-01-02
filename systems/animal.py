import random
from math import sqrt

class AnimalSystem():
    targets = {}

    @staticmethod
    def update(entities, map):
        for entity in entities:
            if 'Animal' in entity:
                if 'Health' in entity:
                    health = entity['Health']

                if 'Health' not in entity or health.is_alive:
                    animal = entity['Animal']
                    if animal.type == "herbivore":
                        AnimalSystem._update_herbivore(entity, entities, map)
                # elif animal.type == "predator":
                #     AnimalSystem._update_predator(entity, entities, map)

    @staticmethod
    def _update_herbivore(entity, entities, map):
        AnimalSystem._update_state(entity)

        AnimalSystem._define_target(entity, entities, map)

        AnimalSystem._action(entity, entities, map)

        # if (hunger and hunger.current_satiety > hunger.max_satiety * 0.8 and 'State' in entity and entity['State'].state != "pregnant"):
        #     partner = AnimalSystem._find_partner(entity, entities)
        #     if partner:
        #         AnimalSystem._breed(entity, partner, entities)

    @staticmethod
    def _update_state(entity):
        hunger = entity['Hunger']

        if hunger.current_satiety > hunger.max_satiety * 0.7:
            entity['state'] = "chill"
        elif hunger.current_satiety <= hunger.max_satiety * 0.7:
            entity['state'] = "hungry"

    @classmethod
    def _define_target(self, entity, entities, map):
        state = entity['state']
        target_id = entity['target_id']

        if state == "hungry" and target_id not in AnimalSystem.targets:
            if AnimalSystem._find_food(entity, entities, map):
                pass # print("Нашёл еду")
            else:
                entity['target_id'] = "nope"
        elif state == "chill":
            entity['target_id'] = "nope"

    @classmethod
    def _action(self, entity, entities, map):
        pos = entity['Position']
        state = entity['state']
        target_id = entity['target_id']

        if state == "hungry" and target_id in AnimalSystem.targets:
            target = AnimalSystem.targets[target_id]
            AnimalSystem._move_towards(entity, entities, target, map)

            if AnimalSystem._distance(pos, target) <= 1:
                AnimalSystem._eat_food(entity, target, entities)
                del AnimalSystem.targets[target_id]

        if state == "chill":
            if random.random() < 0.3:
                AnimalSystem._random_move(entity, map, entities)

    @classmethod
    def _find_food(self, entity, entities, map):
        """Найти ближайшую еду для животного"""
        pos = entity['Position']
        animal = entity['Animal']

        nearest_food = None
        min_distance = len(map)**2

        # Для травоядных ищем растения с ягодами
        if animal.type == "herbivore":
            for other in entities:
                if ('Plant' in other and other['Plant'].is_mature and
                    'Position' in other):
                    food_pos = other['Position']
                    target_id = other['id']
                    AnimalSystem.targets[target_id] = food_pos
                    entity['target_id'] = target_id
                    return True
        return False


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

        if dx != 0 and AnimalSystem._can_move_to(pos.x + dx, pos.y, map, entities):
            new_x = pos.x + dx
        elif dy != 0 and AnimalSystem._can_move_to(pos.x, pos.y + dy, map, entities):
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

            if AnimalSystem._can_move_to(new_x, new_y, map, entities):
                (pos.x, pos.y) = (new_x, new_y)

                # Тратим энергию
                if 'Hunger' in entity:
                    entity['Hunger'].current_satiety -= 0.05
                break

    @staticmethod
    def _eat_food(entity, food_pos, entities):
        if entity['Animal'].type == "herbivore":
            for plant in entities:
                if ('Plant' in plant and 'Position' in plant and
                    plant['Position'].x == food_pos.x and
                    plant['Position'].y == food_pos.y):

                    if 'Hunger' in entity:
                        hunger = entity['Hunger']
                        hunger.current_satiety = min(hunger.max_satiety, hunger.current_satiety + 20)
                        # print(f"🐑 Овца съела ягоды в ({food_pos.x},{food_pos.y})")
                    plant['Plant'].is_mature = False
                    plant['Plant'].growth_stage = 0
                    plant['Renderable'].texture_name = plant['Plant'].growth_stage_texture_names[0]
                    break

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
