import pygame
from textures import TextureManager

class RenderSystem():
    @staticmethod
    def draw(window, entities, texture_manager):
        entities_to_draw = []
        for entity in entities:
            if 'Renderable' in entity and 'Position' in entity:
                entities_to_draw.append(entity)

        entities_to_draw.sort(key=lambda e: e['Renderable'].layer)

        for entity in entities_to_draw:
            window.blit(texture_manager.get(entity['Renderable'].texture_name), (entity['Position'].x * 64, entity['Position'].y * 64))
