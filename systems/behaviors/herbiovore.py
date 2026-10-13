from systems.position import Position
import random


class Herbiovore:
    def __init__(self, D, pathfinding_system):
        self.D = D
        self.pathfinding_system = pathfinding_system
        self.max_finding_dis = 8.0

    def update(self, entity):
        self._update_state(entity)
        self._run_state(entity)

    @staticmethod
    def _update_state(entity):
        hunger = entity['Hunger']
        if hunger.current_satiety > hunger.max_satiety * 0.7:
            entity['state'] = "chill"
        else:
            entity['state'] = "hungry"

    def _run_state(self, entity):
        if entity['state'] == "hungry":
            self._run_hungry_behavior(entity)
        elif entity['state'] == "chill":
            self._clear_target(entity)
            self._run_chill_behavior(entity)

    def _run_hungry_behavior(self, entity):
        self._define_target(entity)
        target = self.D.entities.get(entity['Animal'].target_id)
        if not self._is_food(target):
            self._clear_target(entity)
            self._run_chill_behavior(entity)
            return

        target_pos = target['Position']
        if Position._distance(entity['Position'], target_pos) <= 1:
            self._eat_food(entity, target)
            self._clear_target(entity)
            return

        path_comp = entity['PathComp']
        if (not path_comp.path or path_comp.destination is None
            or Position._distance(path_comp.destination, target_pos) > 1):
            if not self.pathfinding_system.find_path(
                entity, target_pos, self.max_finding_dis, arrival_distance=1
            ):
                entity['MoveComp'].state = 'stop'
                return
        entity['MoveComp'].state = 'path'

    @staticmethod
    def _clear_target(entity):
        entity['Animal'].target_id = None
        entity['PathComp'].clear()
        entity['MoveComp'].state = 'stop'

    @staticmethod
    def _run_chill_behavior(entity):
        if random.random() < 0.3:
            entity['MoveComp'].state = 'rand_move'
        else:
            entity['MoveComp'].state = 'stop'

    def _define_target(self, entity):
        if not self._find_food(entity):
            self._clear_target(entity)

    @staticmethod
    def _is_food(other):
        return (other is not None and other['id'] != 0
                and 'Plant' in other and other['Plant'].is_mature
                and 'Position' in other)

    def _find_food(self, entity):
        pos = entity['Position']
        candidates = []
        for other in self.D.entities.values():
            if self._is_food(other):
                distance = Position._distance(pos, other['Position'])
                if distance <= self.max_finding_dis:
                    candidates.append((distance, other['id']))
        if not candidates:
            return False

        target_id = min(candidates, key=lambda candidate: candidate[0])[1]
        if target_id != entity['Animal'].target_id:
            entity['PathComp'].clear()
        entity['Animal'].target_id = target_id
        return True

    def _eat_food(self, entity, plant):
        if not self._is_food(plant):
            return
        hunger = entity['Hunger']
        hunger.current_satiety = min(hunger.max_satiety, hunger.current_satiety + 20)
        plant['Plant'].is_mature = False
        plant['Plant'].growth_stage = 0
        plant['Renderable'].texture_name = plant['Plant'].growth_stage_texture_names[0]
