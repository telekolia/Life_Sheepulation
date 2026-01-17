from systems.component_class import Component
from systems.behaviors.__init__ import *

animal_behaviors = {'herbivore': Herbiovore,
                    'scavenger': Scavenger
                    }

class Animal(Component):
    def __init__(self, type, max_amount_of_children, adult_texture_name, baby_texture_name, is_ready_to_reproduce=False):
        self.type = type
        self.max_amount_of_children = max_amount_of_children
        self.adult_texture_name = adult_texture_name
        self.baby_texture_name = baby_texture_name
        self.is_ready_to_reproduce = is_ready_to_reproduce

class AnimalSystem():
    targets = {}

    @staticmethod
    def update(entities, map):
        for entity in entities.values():
            if 'Animal' in entity and 'Hunger' in entity and 'Health' in entity and entity['Health'].is_alive:
                behavior_type = entity['Animal'].type
                behavior = animal_behaviors.get(behavior_type)
                if behavior:
                    behavior.update(entity, entities, map)