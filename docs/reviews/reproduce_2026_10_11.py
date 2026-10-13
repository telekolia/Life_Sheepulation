"""Baseline review probes, not desired-behavior regression tests.

Run from the repository root: python docs/reviews/reproduce_2026_10_11.py
Prints JSON; does not edit game state on disk or open a visible window.
After fixes, changed observations are expected. See the review for desired behavior.
"""
import ast
import cProfile
import contextlib
import io
import json
import os
from pathlib import Path
import random
import runpy
import statistics
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if Path.cwd() != ROOT:
    raise SystemExit("Run from the repository root")
sys.path.insert(0, str(ROOT))
# Audit source rather than pre-existing bytecode from earlier development.
sys.pycache_prefix = str(ROOT / "docs" / "reviews" / ".unused_review_cache")
sys.dont_write_bytecode = True
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

with contextlib.redirect_stdout(io.StringIO()):
    import pygame
    from camera import Camera
    from entity_manager import EntityCreator, EntityLoader, EntityManager
    from interface.hud import HUD
    from simulation import Simulation
    from systems import (
        GrowthSystem, PathfindingSystem, Plant, Position, Renderable,
        RenderSystem, Tile, MovementSystem,
    )
    from systems.behaviors.scavenger import Scavenger
    from systems.behaviors.herbiovore import Herbiovore
    from systems.movenent import MovementUtils

results = {}


def probe(name, fn):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            results[name] = fn()
    except Exception as exc:
        results[name] = {"exception": type(exc).__name__, "message": str(exc)}


def load():
    EntityCreator.entity_types.clear()
    EntityLoader.load_directory(EntityCreator.entity_types, "entities")
    return sorted(EntityCreator.entity_types)


def manager():
    em = EntityManager.__new__(EntityManager)
    em.entities = {}
    em.entities_to_spawn = []
    em.total_entities_ever_existed = 0
    em.map = [[{"Tile": Tile("grass")} for _ in range(5)] for _ in range(5)]
    return em


def dependencies(em):
    return SimpleNamespace(entities=em.entities, map=em.map,
                           entity_manager=em, entity_creator=EntityCreator())


def spawn():
    em = manager()
    em.save_spawn_add(EntityCreator.create_entity("baby_sheep", 2, 3))
    em.save_spawn_proccess()
    p = next(iter(em.entities.values()))["Position"]
    return {"requested": [2, 3], "actual": [p.x, p.y]}


def eat_wrong_entity():
    sheep = EntityCreator.create_entity("sheep", 1, 1)
    sheep["id"] = 1
    sheep["Hunger"].current_satiety = 0
    grass = EntityCreator.create_entity("grass_tile", 4, 4)
    grass["id"] = 2
    Scavenger._eat_food(sheep, Position(2, 2), {1: sheep, 2: grass})
    return {"living_eater_id": sheep["id"], "satiety": sheep["Hunger"].current_satiety}


def scavenger_route():
    em = manager()
    eater = EntityCreator.create_entity("hyena", 0, 0)
    eater["Hunger"].current_satiety = 0
    corpse = EntityCreator.create_entity("sheep", 3, 0)
    corpse["Health"].is_alive = False
    em.add(eater)
    em.add(corpse)
    d = dependencies(em)
    Scavenger(d, PathfindingSystem(d)).update(eater)
    return {"move_state": eater["MoveComp"].state, "path_length": len(eater["PathComp"].path)}


def blocked_corpse():
    em = manager()
    eater = EntityCreator.create_entity("hyena", 0, 0)
    corpse = EntityCreator.create_entity("sheep", 3, 0)
    corpse["Health"].is_alive = False
    em.add(eater)
    em.add(corpse)
    eater["PathComp"].target_id = corpse["id"]
    PathfindingSystem(dependencies(em)).find_path(eater)
    return {"target_after_search": eater["PathComp"].target_id, "path_length": len(eater["PathComp"].path)}


def missing_target():
    em = manager()
    eater = EntityCreator.create_entity("sheep", 0, 0)
    em.add(eater)
    eater["PathComp"].target_id = 999
    eater["PathComp"].path = [Position(1, 0)]
    MovementSystem(dependencies(em)).path_movement(eater)


def overlap():
    em = manager()
    stronger = EntityCreator.create_entity("sheep", 0, 0)
    weaker = EntityCreator.create_entity("baby_sheep", 1, 0)
    em.add(stronger)
    em.add(weaker)
    before = MovementUtils._can_move_to(1, 0, em.entities, em.map)
    moved = MovementSystem(dependencies(em)).try_move_to(stronger, Position(1, 0))
    return {"planner_allows": before, "executor_moves": moved,
            "positions_equal": stronger["Position"] == weaker["Position"]}


def growth_overflow():
    plant = {"id": 1, "Plant": Plant(1, ["bush", "berry_bush"]),
             "Renderable": Renderable("bush")}
    with patch("systems.plant.randint", return_value=3):
        GrowthSystem(SimpleNamespace(entities={1: plant})).proccess()


def delayed_death():
    em = manager()
    e = EntityCreator.create_entity("sheep", 0, 0)
    e["Health"].current_hp = 0.1
    e["Hunger"].current_satiety = 0
    em.add(e)
    sim = Simulation(em, EntityCreator(), SimpleNamespace(tick=lambda fps: 200))
    with patch("systems.behaviors.herbiovore.random.random", return_value=1):
        sim.update()
    return {"hp": e["Health"].current_hp, "alive_after_turn": e["Health"].is_alive,
            "age_ticks": e["Age"].time}


def timer_loss():
    em = manager()
    sim = Simulation(em, EntityCreator(), SimpleNamespace(tick=lambda fps: 550))
    calls = []
    sim.systems = [SimpleNamespace(proccess=lambda: calls.append(1))]
    sim.update()
    return {"elapsed_ms": 550, "turns": len(calls), "remainder_s": sim.turn_timer}


def world_smoke():
    random.seed(20261011)
    em = EntityManager()
    sim = Simulation(em, EntityCreator(), SimpleNamespace(tick=lambda fps: 200))
    for _ in range(200):
        sim.update()
    return {"turns": 200, "entities": len(em.entities),
            "alive_animals": sum("Animal" in e and e["Health"].is_alive for e in em.entities.values())}


def main_smoke():
    with patch("pygame.event.get", return_value=[pygame.event.Event(pygame.QUIT)]):
        runpy.run_path("main.py", run_name="__main__")
    return "Startup, one draw and QUIT completed with SDL dummy"


def performance_sample():
    from textures import TextureManager
    random.seed(20261011)
    em = EntityManager()
    initial_count = len(em.entities)
    pygame.init()
    window = pygame.display.set_mode((1920, 1080))
    TextureManager.load_directory("res")
    renderer = RenderSystem(window, Camera((-800, 0), (1920, 1080), .4), em)
    renderer.draw()  # Warm up; draw only, no display update or HUD.
    samples = []
    for _ in range(20):
        start = time.perf_counter()
        renderer.draw()
        samples.append((time.perf_counter() - start) * 1000)
    with patch("pygame.transform.scale", wraps=pygame.transform.scale) as scale:
        renderer.draw()
        scales = scale.call_count
    sim = Simulation(em, EntityCreator(), SimpleNamespace(tick=lambda fps: 200))
    turns = []
    for _ in range(60):
        start = time.perf_counter()
        sim.update()
        turns.append((time.perf_counter() - start) * 1000)
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(10):
        sim.update()
    profiler.disable()
    entries = []
    for entry in profiler.getstats():
        code = entry.code
        if isinstance(code, str) or not code.co_filename.startswith(str(ROOT)):
            continue
        entries.append({"function": str(Path(code.co_filename).relative_to(ROOT)) + ":" + code.co_name,
                        "calls": entry.callcount, "self_ms": round(entry.inlinetime * 1000, 3),
                        "cumulative_ms": round(entry.totaltime * 1000, 3)})
    entries.sort(key=lambda e: e["self_ms"], reverse=True)

    def summary(values):
        ordered = sorted(values)
        return {"median_ms": round(statistics.median(values), 3),
                "p95_ms": round(ordered[int(.95 * (len(ordered) - 1))], 3),
                "samples": len(values)}

    return {"environment": "SDL dummy, logging redirected, one local run; not real-window FPS",
            "initial_entities": initial_count, "scales_per_draw": scales,
            "render_draw_only": summary(samples), "first_60_turns": summary(turns),
            "next_10_turns_profile_top_self_time": entries[:8]}


probe("python_syntax", lambda: [str(p.relative_to(ROOT)) for p in
      sorted(list(ROOT.glob("*.py")) + list((ROOT / "systems").rglob("*.py")) +
             list((ROOT / "interface").rglob("*.py"))) if ast.parse(p.read_text(encoding="utf-8"))])
probe("templates", load)
probe("queued_spawn_position", spawn)
probe("scavenger_eats_living_entity", eat_wrong_entity)
probe("scavenger_missing_route", scavenger_route)
probe("corpse_unreachable_for_planner", blocked_corpse)
probe("deleted_target_lookup", missing_target)
probe("planner_executor_overlap", overlap)
probe("camera_roundtrip", lambda: list(Camera((10, 20), (800, 600), .5).screen_to_world(
    Camera((10, 20), (800, 600), .5).world_to_screen((128, 192)))))
probe("hud_stats_dict", lambda: HUD()._calculate_stats({1: {"type": "sheep"}}))
probe("growth_small_duration", growth_overflow)
probe("death_delayed_one_turn", delayed_death)
probe("turn_timer_loss", timer_loss)
probe("seeded_world_200_turns", world_smoke)
probe("local_performance_sample", performance_sample)
probe("main_dummy_smoke", main_smoke)
print(json.dumps({"python": sys.version.split()[0], "pygame": pygame.version.ver,
                  "results": results}, ensure_ascii=False, indent=2))
