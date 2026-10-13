from systems.position import Position
from systems.path import PathComp
from systems.movenent import MovementUtils
import random


class Scavenger:
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
        if not self._find_food(entity):
            self._run_search_behavior(entity)
            return

        target = self.D.entities.get(entity['Animal'].target_id)
        if not self._is_food(target):
            self._clear_target(entity)
            self._run_search_behavior(entity)
            return

        if Position._distance(entity['Position'], target['Position']) <= 1:
            self._eat_food(entity, target)
            self._clear_target(entity)
        else:
            entity['MoveComp'].state = 'path'

    @staticmethod
    def _clear_target(entity):
        entity['Animal'].target_id = None
        entity['Animal'].is_searching = False
        entity['PathComp'].clear()
        entity['MoveComp'].state = 'stop'

    @staticmethod
    def _run_chill_behavior(entity):
        if random.random() < 0.3:
            entity['MoveComp'].state = 'rand_move'
        else:
            entity['MoveComp'].state = 'stop'

    @staticmethod
    def _is_food(other):
        return (other is not None and other['id'] != 0
                and 'Health' in other and not other['Health'].is_alive
                and 'Position' in other)

    def _next_step_available(self, entity):
        path = entity['PathComp'].path
        if not path:
            return False
        step = path[0]
        return MovementUtils._can_move_to(
            step.x, step.y, self.D.entities, self.D.map
        )

    def _find_food(self, entity):
        pos = entity['Position']
        animal = entity['Animal']
        path_comp = entity['PathComp']
        candidates = []
        for other in self.D.entities.values():
            if self._is_food(other):
                distance = Position._distance(pos, other['Position'])
                if distance <= self.max_finding_dis:
                    candidates.append((distance, other))

        for distance, target in sorted(candidates, key=lambda candidate: candidate[0]):
            if distance <= 1:
                path_comp.clear()
            elif (target['id'] == animal.target_id and not animal.is_searching
                  and path_comp.destination is not None
                  and Position._distance(path_comp.destination, target['Position']) <= 1
                  and self._next_step_available(entity)):
                # The current route still provides a valid approach.
                pass
            else:
                # Plan in a local view so failed candidates cannot erase an
                # ongoing search route. Components other than PathComp are read.
                planning_entity = entity.copy()
                planned_path = PathComp()
                planning_entity['PathComp'] = planned_path
                if not self.pathfinding_system.find_path(
                    planning_entity, target['Position'],
                    max_distanse=None, arrival_distance=1
                ):
                    continue
                path_comp.destination = planned_path.destination
                path_comp.path = planned_path.path

            animal.target_id = target['id']
            animal.is_searching = False
            return True
        return False

    def _run_search_behavior(self, entity):
        animal = entity['Animal']
        path_comp = entity['PathComp']
        animal.target_id = None
        if animal.is_searching and self._next_step_available(entity):
            entity['MoveComp'].state = 'path'
            return

        path_comp.clear()
        animal.is_searching = True
        entity['MoveComp'].state = 'stop'
        reachable = self.pathfinding_system.reachable_positions(
            entity, self.max_finding_dis
        )
        if not reachable:
            return

        pos = entity['Position']
        dx, dy = random.choice([
            (1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1),
        ])

        def direction_score(point):
            offset_x, offset_y = point.x - pos.x, point.y - pos.y
            return (offset_x * dx + offset_y * dy,
                    -abs(offset_x * dy - offset_y * dx))

        best_score = max(direction_score(point) for point in reachable)
        if best_score[0] > 0:
            choices = [point for point in reachable if direction_score(point) == best_score]
        else:
            # A closed direction must not prevent searching elsewhere.
            farthest = max(Position._distance(pos, point) for point in reachable)
            choices = [point for point in reachable
                       if Position._distance(pos, point) == farthest]
        destination = random.choice(choices)
        if self.pathfinding_system.find_path(
            entity, destination, max_distanse=self.max_finding_dis
        ):
            entity['MoveComp'].state = 'path'

    @staticmethod
    def _eat_food(entity, corpse):
        if not Scavenger._is_food(corpse):
            return
        hunger = entity['Hunger']
        hunger.current_satiety = min(hunger.max_satiety, hunger.current_satiety + 20)
        corpse['id'] = 0
