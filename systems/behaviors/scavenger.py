from systems.position import Position
import random

class Scavenger:
    targets = {}

    @staticmethod
    def update(entity, entities, map):
        Scavenger._update_state(entity)

        Scavenger._run_state(entity, entities, map)

    @staticmethod
    def _update_state(entity):
        hunger = entity['Hunger']

        if hunger.current_satiety > hunger.max_satiety * 0.7:
            entity['state'] = "chill"
        elif hunger.current_satiety <= hunger.max_satiety * 0.7:
            entity['state'] = "hungry"


    @staticmethod
    def _run_state(entity, entities, map):
        state = entity['state']

        if state == "hungry":
            Scavenger._run_hungry_behavior(entity,entities, map)
        elif state == "chill":
            Scavenger._run_chill_behavior(entity, entities, map)

    @classmethod
    def _run_hungry_behavior(self, entity, entities, map):
        pos = entity['Position']

        Scavenger._define_target(entity, entities, map)
        if entity['target_id'] == "nope":
            Position._random_move(entity, map, entities)
            return
        
        target_pos = Scavenger.targets[entity['target_id']]

        if Position._distance(pos, target_pos) <= 1:
            Scavenger._eat_food(entity, target_pos, entities)
            del Scavenger.targets[entity['target_id']]
        else:
            Position._move_towards(entity, entities, target_pos, map)
            

    @staticmethod
    def _run_chill_behavior(entity, entities, map):
        if random.random() < 0.3:
            Position._random_move(entity, map, entities)

    @classmethod
    def _define_target(self, entity, entities, map):
        if not Scavenger._find_food(entity, entities, map):
            entity['target_id'] = "nope"

    @classmethod
    def _find_food(self, entity, entities, map):
        """Найти ближайшую еду для животного"""
        pos = entity['Position']
        animal = entity['Animal']

        distanses_to_food_units = []

        for other in entities.values():
            if ('Health' in other and not other['Health'].is_alive and 'Position' in other):
                food_pos = other['Position']
                target_id = other['id']
                distanses_to_food_units.append((target_id, food_pos, Position._distance(pos, food_pos)))

        if len(distanses_to_food_units) == 0:
            return False
        
        target_data = min(distanses_to_food_units, key=lambda x: x[2])
        entity['target_id'] = target_data[0]
        Scavenger.targets[entity['target_id']] = target_data[1]
        return True

    @staticmethod
    def _eat_food(entity, food_pos, entities):
        for corpse in entities.values():
            if ('Health' in corpse and not corpse['Health'].is_alive and
                corpse and 'Position' in corpse and corpse['Position'].x == food_pos.x and corpse['Position'].y == food_pos.y):
                hunger = entity['Hunger']
                hunger.current_satiety = min(hunger.max_satiety, hunger.current_satiety + 20)
                del entities[corpse['id']]
                break
