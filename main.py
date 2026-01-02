import pygame
from world import World
from textures import TextureManager
from interface.hud import HUD
from entity_manager import EntityManager
from tile import Tile

map_size = 15

pygame.init()

window = pygame.display.set_mode((map_size * 64, map_size * 64))
pygame.display.set_caption("Симуляция жизни")

hud = HUD(64)
show_stats = False
show_hud = False

clock = pygame.time.Clock()
turn_timer = 0
turn_delay = 0.5  # секунд между ходами

texture_manager = TextureManager()
texture_manager.load_directory('res')

pygame.display.set_icon(texture_manager.get("sheep"))

default_map = [[Tile("g") for i in range(map_size)] for j in range(map_size)]
for x in range(5, 7):
    for y in range(7, 9):
        default_map[x][y] = Tile("w")
for i in range(1, 9):
    default_map[1][i] = Tile("w")
    default_map[i][1] = Tile("w")

default_entities = []
entity_manager = EntityManager()
entity_manager.load_directory("entities")
entity_manager.batch_spawn(default_entities, default_map, "bush", 15)
entity_manager.batch_spawn(default_entities, default_map, "sheep", 20)

world = World(default_entities, default_map)
world.cout()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    # Handle input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            # Показать/скрыть статистику
            elif event.key == pygame.K_s:
                show_stats = not show_stats
                print("Статистика " + ("вкл" if show_stats else "выкл"))

            # Показать/скрыть HUD
            elif event.key == pygame.K_h:
                show_hud = not show_hud
                print("HUD " + ("вкл" if show_hud else "выкл"))

    # Update
    turn_timer += dt
    if turn_timer >= turn_delay:
        world.update()
        turn_timer = 0

    # Render
    world.draw(window, texture_manager)

    # 2. Рисуем HUD поверх сущностей
    if show_hud:
        hud.draw(window, world.entities)

    # 3. Рисуем статистику в углу
    if show_stats:
        hud.draw_stats(window, world.entities, 10, 10)

    pygame.display.update()

pygame.quit()
