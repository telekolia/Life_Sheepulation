from tile import Tile
import copy
from systems.__init__ import RenderSystem, GrowthSystem, HealthSystem, HungerSystem, AnimalSystem
from entity_manager import EntityManager

class World():
    map = []

    @classmethod
    def __init__(self):
        World.generate_default_map()
        World.generate_default_entities()
        
        print(f"Мир с {len(EntityManager.entities)} сушествами")

    @classmethod
    def generate_default_entities(self):
        EntityManager.batch_spawn(World.map, "bush", 2)
        EntityManager.batch_spawn(World.map, "sheep", 6)
        EntityManager.batch_spawn(World.map, "hyena", 1)

    @classmethod
    def generate_default_map(self):
        map_size = 15
        self.map = [[Tile("g") for i in range(map_size)] for j in range(map_size)]
        for x in range(5, 7):
            for y in range(7, 9):
                self.map[x][y] = Tile("w")
        for i in range(1, 9):
            self.map[1][i] = Tile("w")
            self.map[i][1] = Tile("w")

    @classmethod
    def draw(self, window):
        for i in range(len(self.map)):
            for j in range(len(self.map)):
                self.map[i][j].draw(window, i*64, j*64)

        EntityManager.draw(window)

    @classmethod
    def cout(self):
        print("world map:")
        for y in range(len(self.map)):
            for x in range(len(self.map)):
                print(self.map[x][y].type, end=" ")
            print()
