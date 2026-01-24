from systems.position import Position
from systems.movenent import MovementUtils
import random

class Herbiovore:
    @staticmethod
    def update(entity, entities):
        Herbiovore._update_state(entity)

        Herbiovore._run_state(entity, entities)

    @staticmethod
    def _update_state(entity):
        hunger = entity['Hunger']

        if hunger.current_satiety > hunger.max_satiety * 0.7:
            entity['state'] = "chill"
        elif hunger.current_satiety <= hunger.max_satiety * 0.7:
            entity['state'] = "hungry"


    @staticmethod
    def _run_state(entity, entities):
        state = entity['state']

        if state == "hungry":
            Herbiovore._run_hungry_behavior(entity, entities)
        elif state == "chill":
            Herbiovore._run_chill_behavior(entity)

    @classmethod
    def _run_hungry_behavior(self, entity, entities):
        pos = entity['Position']

        Herbiovore._define_target(entity, entities)
        if entity['target_id'] == "nope":
            Herbiovore._run_chill_behavior(entity)
            return
        
        target = entities[entity['target_id']]
        target_pos = target['Position']

        if Position._distance(pos, target_pos) <= 1:
            Herbiovore._eat_food(entity, target_pos, entities)
            entity['PathComp'].target_id = None
            entity['target_id']= "nope"
        else:
            entity['PathComp'].state = 'path'

    @staticmethod
    def _run_chill_behavior(entity):
        if 'MoveComp' in entity and random.random() < 0.3:
            entity['MoveComp'].state = 'rand_move'
        else:
            entity['MoveComp'].state = 'stop'

    @classmethod
    def _define_target(self, entity, entities):
        if not Herbiovore._find_food(entity, entities):
            entity['target_id'] = "nope"
            entity['PathComp'].target_id = None

    @classmethod
    def _find_food(self, entity, entities):
        """Найти ближайшую еду для животного"""
        pos = entity['Position']
        animal = entity['Animal']

        distanses_to_food_units = []

        for other in entities.values():
            if ('Plant' in other and other['Plant'].is_mature and 'Position' in other):
                food_pos = other['Position']
                target_id = other['id']
                distanses_to_food_units.append((target_id, food_pos, Position._distance(pos, food_pos)))

        if len(distanses_to_food_units) == 0:
            return False
        
        target_data = min(distanses_to_food_units, key=lambda x: x[2])
        entity['target_id'] = target_data[0]
        entity['PathComp'].target_id = target_data[0]
        return True

    @staticmethod
    def _eat_food(entity, food_pos, entities):
        for plant in entities.values():
            if ('Plant' in plant and 'Position' in plant and plant['Position'].x == food_pos.x and plant['Position'].y == food_pos.y):
                hunger = entity['Hunger']
                hunger.current_satiety = min(hunger.max_satiety, hunger.current_satiety + 20)
                plant['Plant'].is_mature = False
                plant['Plant'].growth_stage = 0
                plant['Renderable'].texture_name = plant['Plant'].growth_stage_texture_names[0]
                break
