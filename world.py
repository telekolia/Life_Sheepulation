from tile import Tile
from systems.__init__ import RenderSystem, GrowthSystem, HealthSystem, HungerSystem, AnimalSystem

class World():
    def __init__(self, entities, map):
        self.map = [row[:] for row in map]
        self.entities = [row for row in entities]
        print(f"Мир с {len(entities)} сушествами")

    def update(self):
        HealthSystem.update(self.entities)
        HungerSystem.update(self.entities)
        AnimalSystem.update(self.entities, self.map)
        GrowthSystem.update(self.entities)

    def draw(self, window, texture_manager):
        for i in range(len(self.map)):
            for j in range(len(self.map)):
                self.map[i][j].draw(window, i*64, j*64)

        RenderSystem.draw(window, self.entities, texture_manager)


    def cout(self):
        print("world map:")
        for y in range(len(self.map)):
            for x in range(len(self.map)):
                print(self.map[x][y].type, end=" ")
            print()
