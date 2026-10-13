import contextlib
import io
import json
import random
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pygame

from entity_manager import EntityCreator, EntityLoader, EntityManager
from interface.hud import HUD
from systems.behaviors.herbiovore import Herbiovore
from systems.behaviors.scavenger import Scavenger
from systems.movenent import MovementSystem
from systems.path import PathComp, PathfindingSystem
from systems.plant import Plant
from systems.position import Position
from systems.tile import Tile
from test_scavenger import animal


def world(*entities, size=7, blocked=()):
    grid = [[{'Tile': Tile('grass', is_passable=(x, y) not in blocked)}
             for y in range(size)] for x in range(size)]
    return SimpleNamespace(entities={e['id']: e for e in entities}, map=grid)


def bush(entity_id, x, y):
    return {
        'id': entity_id, 'Position': Position(x, y),
        'Plant': Plant(40, ['bush', 'bush_mature'], is_mature=True),
        'Renderable': SimpleNamespace(texture_name='bush_mature'),
    }


class NavigationTests(unittest.TestCase):
    def setUp(self):
        rng = patch('random.random', return_value=0.5)
        rng.start()
        self.addCleanup(rng.stop)
        direction = patch('random.choice', side_effect=lambda values: values[0])
        direction.start()
        self.addCleanup(direction.stop)
        # Existing movement diagnostics are not part of the test result.
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def test_move_to_point_without_entity_target(self):
        walker = animal(1)
        del walker['Animal']
        D = world(walker)
        self.assertTrue(PathfindingSystem(D).find_path(walker, Position(3, 0)))
        walker['MoveComp'].state = 'path'
        movement = MovementSystem(D)
        for _ in range(3):
            movement.proccess()
        self.assertEqual(walker['Position'], Position(3, 0))
        self.assertEqual(walker['PathComp'].path, [])
        self.assertEqual(walker['MoveComp'].state, 'stop')

    def test_route_survives_target_move_and_removal(self):
        walker = animal(1)
        target = bush(2, 3, 0)
        D = world(walker, target)
        walker['Animal'].target_id = 2
        self.assertTrue(PathfindingSystem(D).find_path(walker, target['Position']))
        target['Position'].x = 6
        del D.entities[2]
        walker['MoveComp'].state = 'path'
        for _ in range(3):
            MovementSystem(D).proccess()
        self.assertEqual(walker['Position'], Position(3, 0))
        self.assertEqual(walker['PathComp'].destination, Position(3, 0))

    def test_already_arrived_is_success_with_empty_path(self):
        walker = animal(1)
        self.assertTrue(PathfindingSystem(world(walker)).find_path(walker, Position(0, 0)))
        self.assertEqual(walker['PathComp'].path, [])
        self.assertEqual(walker['PathComp'].destination, Position(0, 0))

    def test_unreachable_destination_clears_old_route(self):
        walker = animal(1)
        D = world(walker, blocked=[(1, y) for y in range(7)])
        walker['PathComp'].destination = Position(0, 3)
        walker['PathComp'].path = [Position(0, 1)]
        self.assertFalse(PathfindingSystem(D).find_path(walker, Position(3, 0)))
        self.assertEqual(walker['PathComp'].path, [])
        self.assertIsNone(walker['PathComp'].destination)

    def test_radius_boundary_and_out_of_map_destination(self):
        walker = animal(1)
        finder = PathfindingSystem(world(walker))
        self.assertTrue(finder.find_path(walker, Position(2, 0), max_distanse=2))
        self.assertFalse(finder.find_path(walker, Position(3, 0), max_distanse=2))
        self.assertFalse(finder.find_path(walker, Position(-1, 0)))

    def test_path_component_clone_owns_destination_and_steps(self):
        original = PathComp()
        original.destination = Position(3, 0)
        original.path = [Position(1, 0), Position(2, 0), Position(3, 0)]
        cloned = original.clone()
        cloned.destination.x = 5
        cloned.path[0].y = 4
        cloned.path.pop()
        self.assertEqual(original.destination, Position(3, 0))
        self.assertEqual(original.path[0], Position(1, 0))
        self.assertEqual(len(original.path), 3)

    def test_corpse_approach_and_feeding(self):
        eater = animal(1)
        corpse = animal(2, x=3, alive=False)
        D = world(eater, corpse)
        behavior = Scavenger(D, PathfindingSystem(D))
        movement = MovementSystem(D)
        behavior.update(eater)
        self.assertEqual(eater['PathComp'].destination, Position(2, 0))
        for _ in range(3):
            behavior.update(eater)
            movement.proccess()
        self.assertEqual(eater['Position'], Position(2, 0))
        self.assertEqual(eater['Hunger'].current_satiety, 30)
        self.assertEqual(corpse['id'], 0)
        self.assertIsNone(eater['Animal'].target_id)
        self.assertIsNone(eater['PathComp'].destination)
        self.assertEqual(eater['PathComp'].path, [])

    def test_herbivore_approach_and_feeding(self):
        eater = animal(1)
        plant = bush(2, 3, 0)
        D = world(eater, plant)
        behavior = Herbiovore(D, PathfindingSystem(D))
        for _ in range(3):
            behavior.update(eater)
            MovementSystem(D).proccess()
        self.assertEqual(eater['Position'], Position(2, 0))
        self.assertEqual(eater['Hunger'].current_satiety, 30)
        self.assertFalse(plant['Plant'].is_mature)
        self.assertEqual(plant['Plant'].growth_stage, 0)
        self.assertEqual(plant['Renderable'].texture_name, 'bush')
        self.assertIsNone(eater['Animal'].target_id)
        self.assertEqual(eater['PathComp'].path, [])

    def test_consumed_or_removed_food_cancels_food_route(self):
        for kind in ('scavenger', 'herbivore'):
            for removed in (False, True):
                with self.subTest(kind=kind, removed=removed):
                    eater = animal(1)
                    food = animal(2, x=3, alive=False) if kind == 'scavenger' else bush(2, 3, 0)
                    D = world(eater, food)
                    cls = Scavenger if kind == 'scavenger' else Herbiovore
                    behavior = cls(D, PathfindingSystem(D))
                    behavior.update(eater)
                    self.assertTrue(eater['PathComp'].path)
                    if removed:
                        del D.entities[2]
                    elif kind == 'scavenger':
                        food['id'] = 0
                    else:
                        food['Plant'].is_mature = False
                    behavior.update(eater)
                    MovementSystem(D).proccess()
                    self.assertEqual(eater['Hunger'].current_satiety, 10)
                    self.assertIsNone(eater['Animal'].target_id)
                    if kind == 'scavenger':
                        self.assertTrue(eater['Animal'].is_searching)
                        self.assertNotEqual(eater['PathComp'].destination, Position(2, 0))
                        self.assertEqual(Position._distance(eater['Position'], Position(0, 0)), 1)
                    else:
                        self.assertEqual(eater['Position'], Position(0, 0))
                        self.assertIsNone(eater['PathComp'].destination)
                        self.assertEqual(eater['PathComp'].path, [])

    def test_chill_cancels_food_route(self):
        for cls, food in ((Scavenger, animal(2, x=3, alive=False)),
                          (Herbiovore, bush(2, 3, 0))):
            eater = animal(1)
            D = world(eater, food)
            behavior = cls(D, PathfindingSystem(D))
            behavior.update(eater)
            eater['Hunger'].current_satiety = 50
            behavior.update(eater)
            self.assertIsNone(eater['Animal'].target_id)
            self.assertEqual(eater['PathComp'].path, [])
            self.assertEqual(eater['MoveComp'].state, 'stop')

    def test_blocked_food_is_not_consumed(self):
        for cls, food in ((Scavenger, animal(2, x=3, alive=False)),
                          (Herbiovore, bush(2, 3, 0))):
            eater = animal(1)
            D = world(eater, food, blocked=[(1, y) for y in range(7)])
            behavior = cls(D, PathfindingSystem(D))
            behavior.update(eater)
            if cls is Scavenger:
                self.assertIsNone(eater['Animal'].target_id)
                self.assertTrue(eater['Animal'].is_searching)
                self.assertEqual(eater['MoveComp'].state, 'path')
                self.assertTrue(eater['PathComp'].path)
            else:
                self.assertEqual(eater['Animal'].target_id, 2)
                self.assertEqual(eater['MoveComp'].state, 'stop')
                self.assertEqual(eater['PathComp'].path, [])
            self.assertEqual(eater['Hunger'].current_satiety, 10)

    def test_ready_route_is_reused_until_food_moves_out_of_zone(self):
        eater = animal(1)
        food = bush(2, 3, 0)
        D = world(eater, food)
        finder = PathfindingSystem(D)
        behavior = Herbiovore(D, finder)
        with patch.object(finder, 'find_path', wraps=finder.find_path) as find:
            behavior.update(eater)
            behavior.update(eater)
            self.assertEqual(find.call_count, 1)
            food['Position'].y = 3
            behavior.update(eater)
            self.assertEqual(find.call_count, 2)
        self.assertLessEqual(Position._distance(eater['PathComp'].destination, food['Position']), 1)


class IntegrationTests(unittest.TestCase):
    def test_json_templates_load_clone_and_have_single_target_owner(self):
        templates = {}
        with contextlib.redirect_stdout(io.StringIO()):
            EntityLoader.load_directory(templates, 'entities')
        self.assertEqual(len(templates), 6)
        for file in Path('entities').rglob('*.json'):
            data = json.loads(file.read_text(encoding='utf-8'))
            self.assertNotIn('target_id', data)
        for template in templates.values():
            entity = EntityCreator._create_entity_from_template(template)
            self.assertNotIn('target_id', entity)
            if 'Animal' in entity:
                self.assertIsNone(entity['Animal'].target_id)
                self.assertFalse(hasattr(entity['PathComp'], 'target_id'))

    def test_hud_reads_target_from_animal(self):
        pygame.font.init()
        eater = animal(1, x=2, y=2)
        eater['type'] = 'hyena'
        eater['Animal'].target_id = 42
        surface = pygame.Surface((400, 300))
        font = SimpleNamespace(render=lambda *args: pygame.Surface((50, 10)))
        with patch('pygame.font.Font', return_value=font), patch.object(font, 'render', wraps=font.render) as render:
            HUD().draw(surface, {1: eater})
        self.assertIn('target: 42', [call.args[0] for call in render.call_args_list])

    def test_default_world_runs_fixed_turns(self):
        from simulation import Simulation
        previous_templates = EntityCreator.entity_types
        previous_rng = random.getstate()
        self.addCleanup(setattr, EntityCreator, 'entity_types', previous_templates)
        self.addCleanup(random.setstate, previous_rng)
        EntityCreator.entity_types = {}
        random.seed(20261011)
        with contextlib.redirect_stdout(io.StringIO()):
            EntityLoader.load_directory(EntityCreator.entity_types, 'entities')
            manager = EntityManager()
            simulation = Simulation(manager, EntityCreator(), SimpleNamespace(tick=lambda fps: 200))
            for _ in range(30):
                simulation.update()
        self.assertTrue(manager.entities)
        self.assertTrue(all(key == entity['id'] for key, entity in manager.entities.items()))


if __name__ == '__main__':
    unittest.main()
