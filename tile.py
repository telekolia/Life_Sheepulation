from textures import TileTextures
import pygame

class Tile():
    def __init__(self, type):
        self.type = type
        if self.type == "g":
            self.passable = True
        if self.type == "w":
            self.passable = False

    def draw(self, window, x, y):
        if self.type == "g":
            window.blit(TileTextures.grass, (x, y))
        if self.type == "w":
            window.blit(TileTextures.water, (x , y))
