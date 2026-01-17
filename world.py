from systems.tile import Tile
import copy
from systems.__init__ import RenderSystem, GrowthSystem, HealthSystem, HungerSystem, AnimalSystem
from entity_manager import EntityManager

class World():
    def __init__(self, entity_manager):
        self.map_size = 15
        self.entity_manager = entity_manager
        self.entities = entity_manager.entities
        self.map = [[None for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.generate_default_map()
        
        print(f"Мир с {len(self.entities)} сушествами")

    def generate_default_map(self):
        water_positions = []

        for x in range(5, 7):
            for y in range(7, 9):
                water_positions.append((x, y))
        for i in range(1, 9):
            water_positions.append((1, i))
            water_positions.append((i, 1))

        for x in range(self.map_size):
            for y in range(self.map_size):
                if (x, y) in water_positions:
                    self.entity_manager.spawn("water_tile", x, y)
                else:
                    self.entity_manager.spawn("grass_tile", x, y)

        for entity in self.entities.values():
            if "Tile" in entity and "Position" in entity:
                pos = entity["Position"]
                self.map[pos.x][pos.y] = entity
                # print(f"получилось {pos.x},{pos.y}")
                
    def cout(self):
        print("world map:")
        for y in range(len(self.map)):
            for x in range(len(self.map)):
                print(self.map[x][y]["id"], end=" ")
            print()
