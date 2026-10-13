"""Text-only scenario: python -B tests/trace_scavenger_search.py (from root)."""
import contextlib
import io
import json
import random
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from systems.behaviors.scavenger import Scavenger
from systems.movenent import MovementSystem
from systems.path import PathfindingSystem
from test_navigation import world
from test_scavenger import animal


def trace():
    eater = animal(1, x=1, y=1)
    corpse = animal(2, x=12, y=1, alive=False)
    D = world(eater, corpse, size=16)
    behavior = Scavenger(D, PathfindingSystem(D))
    movement = MovementSystem(D)
    rng = random.Random(20261011)
    saw_search = saw_food = False
    for turn in range(1, 20):
        with patch('systems.behaviors.scavenger.random.choice', side_effect=rng.choice):
            behavior.update(eater)
        with contextlib.redirect_stdout(io.StringIO()):
            movement.proccess()
        pos = eater['Position']
        destination = eater['PathComp'].destination
        saw_search |= eater['Animal'].is_searching
        saw_food |= eater['Animal'].target_id == 2
        print(json.dumps({
            'turn': turn, 'position': [pos.x, pos.y], 'state': eater['state'],
            'searching': eater['Animal'].is_searching,
            'target_id': eater['Animal'].target_id,
            'destination': [destination.x, destination.y] if destination else None,
            'steps_left': len(eater['PathComp'].path),
            'satiety': eater['Hunger'].current_satiety, 'corpse_id': corpse['id'],
        }))
        if corpse['id'] == 0:
            assert saw_search and saw_food
            assert eater['Hunger'].current_satiety == 30
            print('OK: searched, detected food within radius, approached and ate once')
            return
    raise AssertionError('Scenario did not reach food within 19 turns')


if __name__ == '__main__':
    trace()
