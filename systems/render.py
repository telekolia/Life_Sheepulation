from systems.component_class import Component

import pygame
from textures import TextureManager

class Renderable(Component):
    def __init__(self, texture_name, layer = 0):
        self.texture_name = texture_name
        self.layer = layer

class RenderSystem():
    @staticmethod
    def draw(window, entities):
        entities_to_draw = []
        for entity in entities.values():
            if 'Renderable' in entity and 'Position' in entity:
                entities_to_draw.append(entity)

        entities_to_draw.sort(key=lambda e: e['Renderable'].layer)

        for entity in entities_to_draw:
            window.blit(TextureManager.get(entity['Renderable'].texture_name), (entity['Position'].x * 64, entity['Position'].y * 64))
