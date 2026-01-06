from systems.component_class import Component
from systems.behaviors.herbiovore import Herbiovore
from systems.behaviors.scavenger import Scavenger

import random
from math import sqrt

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
            if 'Animal' in entity and 'Hunger' in entity and 'Health' in entity:
                animal = entity['Animal']
                if animal.type == "herbivore":
                    Herbiovore.update(entity, entities, map)
                elif animal.type == "scavenger":
                    Scavenger.update(entity, entities, map)
                # elif animal.type == "predator":
                #   Predator._update(entity, entities, map)