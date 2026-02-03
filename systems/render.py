from systems.component_class import Component

import pygame
from textures import TextureManager

class Renderable(Component):
    def __init__(self, texture_name, layer = 0):
        self.texture_name = texture_name
        self.layer = layer

class RenderSystem():
    def __init__(self, window, camera, entity_manager):
        self.window = window
        self.camera = camera
        self.entity_manager = entity_manager

    def draw(self):
        entities_to_draw = []
        for entity in self.entity_manager.entities.values():
            if 'Renderable' in entity and 'Position' in entity:
                entities_to_draw.append(entity)

        entities_to_draw.sort(key=lambda e: e['Renderable'].layer)

        for entity in entities_to_draw:
            pos = entity['Position']
            x, y = pos.x * 64, pos.y * 64
            world_pos = self.camera.world_to_screen((x, y))

            texture = TextureManager.get(entity['Renderable'].texture_name)
            width, height = texture.get_size()
            scaled_width = int(width * self.camera.zoom)
            scaled_height = int(height * self.camera.zoom)
            scaled_texture = pygame.transform.scale(texture, (scaled_width, scaled_height))

            self.window.blit(scaled_texture, world_pos)
