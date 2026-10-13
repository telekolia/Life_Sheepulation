"""Run from the project root: python -m unittest discover -s tests -v."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from systems.behaviors.scavenger import Scavenger
from systems.health import Health
from systems.hunger import Hunger
from systems.position import Position
from systems.path import PathComp, PathfindingSystem
from systems.movenent import MoveComp
from systems.tile import Tile


def animal(entity_id, x=0, y=0, alive=True, satiety=10):
    return {
        'id': entity_id,
        'Position': Position(x, y),
        'Health': Health(10, 10, 'dead', is_alive=alive),
        'Hunger': Hunger(satiety, 50),
        'Animal': SimpleNamespace(target_id=None, is_searching=False),
        'PathComp': PathComp(),
        'MoveComp': MoveComp(),
    }


class ScavengerTests(unittest.TestCase):
    def setUp(self):
        # Fix the chill decision without modifying the global RNG state.
        rng = patch('systems.behaviors.scavenger.random.random', return_value=0.5)
        rng.start()
        self.addCleanup(rng.stop)
        direction = patch('systems.behaviors.scavenger.random.choice', side_effect=lambda values: values[0])
        direction.start()
        self.addCleanup(direction.stop)

    def run_behavior(self, eater, world):
        D = SimpleNamespace(
            entities=world,
            map=[[{'Tile': Tile('grass')} for _ in range(5)] for _ in range(5)],
        )
        Scavenger(D, PathfindingSystem(D))._run_hungry_behavior(eater)

    def test_nearby_corpse_feeds_once_and_remains_until_cleanup(self):
        eater = animal(1)
        second_eater = animal(2)
        corpse = animal(3, x=1, alive=False)
        world = {1: eater, 2: second_eater, 3: corpse}
        self.run_behavior(eater, world)
        self.run_behavior(second_eater, world)
        self.assertEqual(eater['Hunger'].current_satiety, 30)
        self.assertEqual(second_eater['Hunger'].current_satiety, 10)
        self.assertEqual(corpse['id'], 0)
        self.assertIs(world[3], corpse)
        self.assertIsNone(eater['Animal'].target_id)
        self.assertIsNone(eater['PathComp'].destination)
        self.assertIsNone(second_eater['Animal'].target_id)
        self.assertTrue(second_eater['Animal'].is_searching)
        self.assertTrue(second_eater['PathComp'].path)

    def test_eats_passed_corpse_when_another_shares_its_cell(self):
        eater = animal(1)
        first = animal(2, x=1, alive=False)
        selected = animal(3, x=1, alive=False)
        Scavenger._eat_food(eater, selected)
        self.assertEqual(first['id'], 2)
        self.assertEqual(selected['id'], 0)
        self.assertEqual(eater['Hunger'].current_satiety, 30)

    def test_invalid_food_does_not_feed_or_delete(self):
        for food in (None, animal(2), animal(0, alive=False),
                     {'id': 3, 'Position': Position(0, 0)},
                     {'id': 4, 'Health': Health(0, 10, 'dead', is_alive=False)}):
            with self.subTest(food=food):
                eater = animal(1)
                before_id = food['id'] if food is not None else None
                Scavenger._eat_food(eater, food)
                self.assertEqual(eater['Hunger'].current_satiety, 10)
                if food is not None:
                    self.assertEqual(food['id'], before_id)

    def test_satiety_is_capped(self):
        eater = animal(1, satiety=45)
        Scavenger._eat_food(eater, animal(2, alive=False))
        self.assertEqual(eater['Hunger'].current_satiety, 50)

    def test_skips_consumed_corpse_and_selects_available_one(self):
        eater = animal(1)
        consumed = animal(0, alive=False)
        available = animal(3, x=1, alive=False)
        self.run_behavior(eater, {1: eater, 2: consumed, 3: available})
        self.assertEqual(available['id'], 0)
        self.assertEqual(eater['Hunger'].current_satiety, 30)

    def test_removed_previous_target_is_cleared(self):
        eater = animal(1)
        eater['Animal'].target_id = 99
        eater['PathComp'].destination = Position(3, 0)
        eater['PathComp'].path = [Position(1, 0)]
        self.run_behavior(eater, {1: eater})
        self.assertEqual(eater['Animal'].target_id, None)
        self.assertTrue(eater['Animal'].is_searching)
        self.assertNotEqual(eater['PathComp'].destination, Position(3, 0))
        self.assertTrue(eater['PathComp'].path)
        self.assertEqual(eater['Hunger'].current_satiety, 10)

    def test_distant_corpse_is_not_consumed(self):
        eater = animal(1)
        corpse = animal(2, x=2, alive=False)
        self.run_behavior(eater, {1: eater, 2: corpse})
        self.assertEqual(eater['Animal'].target_id, 2)
        self.assertEqual(eater['MoveComp'].state, 'path')
        self.assertEqual(eater['Hunger'].current_satiety, 10)
        self.assertEqual(corpse['id'], 2)


if __name__ == '__main__':
    unittest.main()
