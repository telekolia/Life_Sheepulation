"""Visible main.py smoke: toggle HUD, draw frames, close automatically.

Run from the project root: python -B tests/smoke_window.py
This opens a real window, rather than the SDL dummy driver.
"""
import contextlib
import io
import random
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame
from interface.hud import HUD

get_events = pygame.event.get
draw_hud = HUD.draw
frames = 0
hud_frames = 0
video_driver = None


def events():
    global frames, video_driver
    frames += 1
    video_driver = pygame.display.get_driver()
    pending = get_events()
    if frames == 2:
        pending.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    if frames == 120:
        pending.append(pygame.event.Event(pygame.QUIT))
    return pending


def hud_draw(self, surface, entities):
    global hud_frames
    hud_frames += 1
    return draw_hud(self, surface, entities)


random.seed(20261011)
with contextlib.redirect_stdout(io.StringIO()), patch('pygame.event.get', events), patch.object(HUD, 'draw', hud_draw):
    result = runpy.run_path('main.py', run_name='__main__')

assert video_driver != 'dummy', video_driver
assert result['show_hud'] is True
assert hud_frames >= 100, hud_frames
print(f'OK: real driver={video_driver}, frames={frames}, HUD frames={hud_frames}')
