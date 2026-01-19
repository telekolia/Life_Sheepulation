from systems.__init__ import *

class Simulation:
    def __init__(self, entity_manager, entity_creator, clock, turn_delay=0.2):
        self.entity_manager = entity_manager
        self.entity_creator = entity_creator
        self.map = self.entity_manager.map
        self.entities = self.entity_manager.entities
        self.clock = clock
        self.turn_timer = 0
        self.turn_delay = turn_delay
        self.init_systems()

    def update(self):
        dt = self.clock.tick(60) / 1000.0
        # Update
        self.turn_timer += dt
        if self.turn_timer >= self.turn_delay:
            HealthSystem.update(self.entities)
            HungerSystem.update(self.entities)
            self.animal_system.update()
            GrowthSystem.update(self.entities)
            AgeSystem.update(self.entities)
            
            self.entity_manager._delete_destroed_entities()
            self.turn_timer = 0

    def init_systems(self):
        self.animal_system = AnimalSystem(self.entities, self.map, self.entity_creator)