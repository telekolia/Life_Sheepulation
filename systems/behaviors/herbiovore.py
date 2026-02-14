from systems.position import Position
from systems.movenent import MovementUtils
import random

class Herbiovore:
    def __init__(self, D, pathfinding_system):
        self.D = D
        self.pathfinding_system = pathfinding_system
        self.max_finding_dis = 8.0

    def update(self, entity):
        self._update_state(entity)

        self._run_state(entity)

    def _update_state(self, entity):
        hunger = entity['Hunger']

        if hunger.current_satiety > hunger.max_satiety * 0.7:
            entity['state'] = "chill"
        elif hunger.current_satiety <= hunger.max_satiety * 0.7:
            entity['state'] = "hungry"


    def _run_state(self, entity):
        state = entity['state']

        if state == "hungry":
            self._run_hungry_behavior(entity)
        elif state == "chill":
            self._run_chill_behavior(entity)

    def _run_hungry_behavior(self, entity):
        pos = entity['Position']

        self._define_target(entity)
        if entity['target_id'] == "nope":
            self._run_chill_behavior(entity)
            return
        
        target = self.D.entities[entity['target_id']]
        target_pos = target['Position']

        if Position._distance(pos, target_pos) <= 1:
            self._eat_food(entity, target_pos)
            entity['PathComp'].target_id = None
            entity['target_id']= "nope"
        else:
            entity['MoveComp'].state = 'path'
            # entity['PathComp'].state = 'path'

    def _run_chill_behavior(self, entity):
        if 'MoveComp' in entity and random.random() < 0.3:
            entity['MoveComp'].state = 'rand_move'
        else:
            entity['MoveComp'].state = 'stop'

    def _define_target(self, entity):
        if not self._find_food(entity):
            entity['target_id'] = "nope"
            entity['PathComp'].target_id = None

    def _find_food(self, entity):
        """Найти ближайшую еду для животного"""
        pos = entity['Position']
        animal = entity['Animal']

        distanses_to_food_units = []

        for other in self.D.entities.values():
            if ('Plant' in other and other['Plant'].is_mature and 'Position' in other):
                food_pos = other['Position']
                target_id = other['id']

                if Position._distance(pos, food_pos) > self.max_finding_dis:
                    continue

                distanses_to_food_units.append((target_id, food_pos, Position._distance(pos, food_pos)))

        if len(distanses_to_food_units) == 0:
            return False
        
        target_data = min(distanses_to_food_units, key=lambda x: x[2])
        best_target_id = target_data[0]
        if best_target_id != entity['PathComp'].target_id:
            entity['target_id'] = target_data[0]
            entity['PathComp'].target_id = target_data[0]
            self.pathfinding_system.find_path(entity, self.max_finding_dis)

        return True

    def _eat_food(self, entity, food_pos):
        for plant in self.D.entities.values():
            if ('Plant' in plant and 'Position' in plant and plant['Position'].x == food_pos.x and plant['Position'].y == food_pos.y):
                hunger = entity['Hunger']
                hunger.current_satiety = min(hunger.max_satiety, hunger.current_satiety + 20)
                plant['Plant'].is_mature = False
                plant['Plant'].growth_stage = 0
                plant['Renderable'].texture_name = plant['Plant'].growth_stage_texture_names[0]
                entity['target_id'] = "nope"
                entity['PathComp'].target_id = None
                break
