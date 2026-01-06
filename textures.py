import pygame
from pathlib import Path

class TileTextures():
    grass = pygame.image.load("res/grass.png")
    water = pygame.image.load("res/water.png")


class TextureManager:
    textures = {}

    @classmethod
    def load_directory(self, directory_path, recursive = True):
        path = Path(directory_path)

        if recursive:
            files = path.rglob("*.png")
        else:
            files = path.glob("*.png")

        for file_path in files:
            texture_name = file_path.stem
            try:
                texture = pygame.image.load(str(file_path))
                TextureManager.textures[texture_name] = texture
                print(f"Loaded texture: {texture_name}")
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")

    @classmethod
    def get(self, texture_name):
        return TextureManager.textures[texture_name]
