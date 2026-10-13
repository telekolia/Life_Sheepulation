import contextlib
import io
import random
import unittest
from unittest.mock import patch

from systems.behaviors.scavenger import Scavenger
from systems.movenent import MovementSystem
from systems.path import PathfindingSystem
from systems.position import Position
from test_navigation import world
from test_scavenger import animal


class ScavengerSearchTests(unittest.TestCase):
    def setUp(self):
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)
        direction = patch('random.choice', side_effect=lambda values: values[0])
        self.choice = direction.start()
        self.addCleanup(direction.stop)

    def behavior(self, eater, *others, size=20, blocked=(), radius=8):
        D = world(eater, *others, size=size, blocked=blocked)
        behavior = Scavenger(D, PathfindingSystem(D))
        behavior.max_finding_dis = radius
        return D, behavior

    def test_corpse_at_radius_is_selected(self):
        eater = animal(1)
        corpse = animal(2, x=8, alive=False)
        _, behavior = self.behavior(eater, corpse)
        behavior.update(eater)
        self.assertEqual(eater['Animal'].target_id, 2)
        self.assertFalse(eater['Animal'].is_searching)
        self.assertEqual(eater['PathComp'].destination, Position(7, 0))

    def test_corpse_beyond_radius_is_not_selected(self):
        eater = animal(1)
        corpse = animal(2, x=9, alive=False)
        _, behavior = self.behavior(eater, corpse)
        behavior.update(eater)
        self.assertIsNone(eater['Animal'].target_id)
        self.assertTrue(eater['Animal'].is_searching)
        self.assertEqual(eater['PathComp'].destination, Position(8, 0))

    def test_radius_uses_euclidean_distance(self):
        for x, y, found in ((3, 4, True), (4, 4, False)):
            with self.subTest(x=x, y=y):
                eater = animal(1)
                _, behavior = self.behavior(eater, animal(2, x=x, y=y, alive=False), radius=5)
                behavior.update(eater)
                self.assertEqual(eater['Animal'].target_id is not None, found)

    def test_farther_accessible_corpse_wins_over_blocked_nearest(self):
        eater = animal(1)
        nearest = animal(2, x=2, y=0, alive=False)
        accessible = animal(3, x=0, y=4, alive=False)
        wall = [(1, y) for y in range(7)]
        _, behavior = self.behavior(eater, nearest, accessible, size=7, blocked=wall)
        behavior.update(eater)
        self.assertEqual(eater['Animal'].target_id, 3)
        self.assertEqual(eater['PathComp'].destination, Position(0, 3))
        self.assertFalse(eater['Animal'].is_searching)

    def test_no_food_searches_to_radius_in_selected_direction(self):
        eater = animal(1, x=5, y=5)
        _, behavior = self.behavior(eater)
        with patch.object(behavior, '_run_chill_behavior') as chill:
            behavior.update(eater)
        chill.assert_not_called()
        self.assertEqual(eater['state'], 'hungry')
        self.assertEqual(eater['MoveComp'].state, 'path')
        self.assertEqual(eater['PathComp'].destination, Position(13, 5))
        self.assertTrue(eater['Animal'].is_searching)
        for step in eater['PathComp'].path:
            self.assertLessEqual(Position._distance(Position(5, 5), step), 8)

    def test_search_route_is_kept_between_turns(self):
        eater = animal(1)
        D, behavior = self.behavior(eater)
        behavior.update(eater)
        destination = eater['PathComp'].destination
        choices_before = self.choice.call_count
        MovementSystem(D).proccess()
        behavior.update(eater)
        self.assertIs(eater['PathComp'].destination, destination)
        self.assertEqual(len(eater['PathComp'].path), 7)
        self.assertEqual(self.choice.call_count, choices_before)

    def test_failed_food_probe_does_not_erase_search_route(self):
        eater = animal(1)
        corpse = animal(2, x=2, alive=False)
        D, behavior = self.behavior(eater, corpse, size=7, blocked=[(1, y) for y in range(7)])
        behavior.update(eater)
        destination = eater['PathComp'].destination
        MovementSystem(D).proccess()
        behavior.update(eater)
        self.assertIs(eater['PathComp'].destination, destination)
        self.assertIsNone(eater['Animal'].target_id)
        self.assertTrue(eater['PathComp'].path)

    def test_food_detected_along_search_route_interrupts_search(self):
        eater = animal(1)
        corpse = animal(2, x=10, alive=False)
        D, behavior = self.behavior(eater, corpse)
        movement = MovementSystem(D)
        behavior.update(eater)
        self.assertEqual(eater['PathComp'].destination, Position(8, 0))
        for _ in range(2):
            movement.proccess()
            behavior.update(eater)
        self.assertEqual(eater['Position'], Position(2, 0))
        self.assertEqual(eater['Animal'].target_id, 2)
        self.assertFalse(eater['Animal'].is_searching)
        self.assertEqual(eater['PathComp'].destination, Position(9, 0))

    def test_finished_search_gets_a_new_destination(self):
        eater = animal(1)
        D, behavior = self.behavior(eater, radius=2)
        behavior.update(eater)
        for _ in range(2):
            MovementSystem(D).proccess()
        self.assertEqual(eater['Position'], Position(2, 0))
        self.assertEqual(eater['PathComp'].path, [])
        behavior.update(eater)
        self.assertEqual(eater['PathComp'].destination, Position(4, 0))
        self.assertEqual(eater['MoveComp'].state, 'path')

    def test_blocked_next_search_step_is_replanned(self):
        eater = animal(1)
        D, behavior = self.behavior(eater)
        behavior.update(eater)
        D.map[1][0]['Tile'].is_passable = False
        behavior.update(eater)
        self.assertNotEqual(eater['PathComp'].path[0], Position(1, 0))
        MovementSystem(D).proccess()
        self.assertEqual(eater['Position'], Position(0, 1))

    def test_small_map_uses_a_shorter_reachable_route(self):
        eater = animal(1)
        _, behavior = self.behavior(eater, size=3)
        behavior.update(eater)
        self.assertEqual(eater['PathComp'].destination, Position(2, 0))
        self.assertEqual(len(eater['PathComp'].path), 2)

    def test_fully_blocked_or_zero_radius_stays_hungry(self):
        for blocked, radius in (([(1, 0), (0, 1)], 8), ([], 0)):
            eater = animal(1)
            D, behavior = self.behavior(eater, blocked=blocked, radius=radius)
            behavior.update(eater)
            MovementSystem(D).proccess()
            self.assertEqual(eater['state'], 'hungry')
            self.assertTrue(eater['Animal'].is_searching)
            self.assertEqual(eater['MoveComp'].state, 'stop')
            self.assertIsNone(eater['PathComp'].destination)
            self.assertEqual(eater['Position'], Position(0, 0))

    def test_sated_animal_cancels_search_and_uses_chill_probability(self):
        eater = animal(1)
        _, behavior = self.behavior(eater)
        behavior.update(eater)
        eater['Hunger'].current_satiety = 36
        with patch('random.random', return_value=0.1):
            behavior.update(eater)
        self.assertEqual(eater['state'], 'chill')
        self.assertFalse(eater['Animal'].is_searching)
        self.assertIsNone(eater['PathComp'].destination)
        self.assertEqual(eater['MoveComp'].state, 'rand_move')

    def test_reachable_positions_respect_radius_and_do_not_mutate_route(self):
        eater = animal(1)
        D, _ = self.behavior(eater, size=5, blocked=[(1, y) for y in range(5)])
        eater['PathComp'].destination = Position(0, 2)
        eater['PathComp'].path = [Position(0, 1), Position(0, 2)]
        reachable = PathfindingSystem(D).reachable_positions(eater, 3)
        self.assertEqual(reachable, [Position(0, 1), Position(0, 2), Position(0, 3)])
        self.assertEqual(eater['PathComp'].destination, Position(0, 2))
        self.assertEqual(len(eater['PathComp'].path), 2)

    def test_fixed_seed_reproduces_choices_and_movement(self):
        def run():
            eater = animal(1, x=4, y=4)
            D, behavior = self.behavior(eater, size=13, radius=3)
            rng = random.Random(20261011)
            snapshots = []
            with patch('systems.behaviors.scavenger.random.choice', side_effect=rng.choice):
                for _ in range(10):
                    behavior.update(eater)
                    MovementSystem(D).proccess()
                    pos = eater['Position']
                    destination = eater['PathComp'].destination
                    snapshots.append((pos.x, pos.y, destination.x, destination.y,
                                      len(eater['PathComp'].path)))
            return snapshots
        self.assertEqual(run(), run())


if __name__ == '__main__':
    unittest.main()
