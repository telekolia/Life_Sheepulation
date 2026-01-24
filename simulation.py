from systems.__init__ import *

class D:
    """
    Class wich store most valuable dependensies in game
    """
    def __init__(self, entity_manager, entity_creator):
        self.entity_manager = entity_manager
        self.entity_creator = entity_creator
        self.map = self.entity_manager.map
        self.entities = self.entity_manager.entities

class Simulation:
    def __init__(self, entity_manager, entity_creator, clock, turn_delay=0.2):
        self.D = D(entity_manager, entity_creator)
        self.clock = clock
        self.turn_timer = 0
        self.turn_delay = turn_delay
        self.init_systems()

    def update(self):
        dt = self.clock.tick(60) / 1000.0
        # Update
        self.turn_timer += dt
        if self.turn_timer >= self.turn_delay:
            
            for system in self.systems:
                system.update()
            
            self.D.entity_manager._delete_destroed_entities()
            self.D.entity_manager.save_spawn_proccess()
            self.turn_timer = 0

    def init_systems(self):
        self.systems = [HealthSystem(self.D),
                        HungerSystem(self.D),
                        AnimalSystem(self.D),
                        GrowthSystem(self.D),
                        AgeSystem(self.D)
                        ]