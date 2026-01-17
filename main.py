import pygame
from world import World
from textures import TextureManager
from interface.hud import HUD
from entity_manager import EntityManager, EntityLoader, EntityCreator

# import json
# from pathlib import Path
# TO DO: реализовать конфиг для быстрого и удобного создания карты и кол-ва и типов мобов для спавна
#        или же... реализовать спавн кликом мышки, как и изменение карты
TextureManager.load_directory('res')
EntityLoader.load_directory(EntityCreator.entity_types, "entities")

entity_manager = EntityManager()
map_size = entity_manager.map_size

hud = HUD(64)
show_stats = False
show_hud = False

pygame.init()

window = pygame.display.set_mode((map_size * 64, map_size * 64))
pygame.display.set_caption("Симуляция жизни")

pygame.display.set_icon(TextureManager.get("sheep"))

clock = pygame.time.Clock()
turn_timer = 0
turn_delay = 0.2  # секунд между ходами

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
        entity_manager.update()
        # print(f"Update {turn_timer}")
        turn_timer = 0

    # Render
    entity_manager.draw(window)

    # 2. Рисуем HUD поверх сущностей
    if show_hud:
        hud.draw(window, entity_manager.entities)

    # 3. Рисуем статистику в углу
    if show_stats:
        hud.draw_stats(window, entity_manager.entities, 10, 10)

    pygame.display.update()

pygame.quit()
