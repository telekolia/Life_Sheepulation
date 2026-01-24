from systems.component_class import Component
from systems.behaviors.__init__ import *
from random import shuffle
from systems.movenent import Movement

animal_behaviors = {'herbivore': Herbiovore,
                    'scavenger': Scavenger
                    }

class Animal(Component):
    def __init__(self, type, max_amount_of_children, adult_name, baby_name, adult_age, death_age, is_ready_to_reproduce=False):
        self.type = type
        self.max_amount_of_children = max_amount_of_children
        self.adult_name = adult_name
        self.baby_name = baby_name
        self.adult_age = adult_age
        self.death_age = death_age
        self.is_ready_to_reproduce = is_ready_to_reproduce

class AnimalSystem():
    def __init__(self, D):
        self.D = D

    def update(self):
        for entity in self.D.entities.values():
            if 'Animal' in entity and 'Hunger' in entity and 'Health' in entity and entity['Health'].is_alive:
                behavior_type = entity['Animal'].type
                behavior = animal_behaviors.get(behavior_type)
                if behavior:
                    behavior.update(entity, self.D.entities, self.D.map)

                self.proccess_age(entity)

    def proccess_age(self, entity):
        if 'Age' in entity and 'Animal' in entity:
            animal = entity['Animal']
            age = entity['Age']
            
            if age.year >= animal.adult_age and entity['type'] == animal.baby_name:
                self.become_adult(entity)
            
            if age.year >= animal.death_age:
                entity['Health'].current_hp -= min(entity['Health'].current_hp, 0.5)
                # print("Умирает")

    def become_adult(self, entity):
        animal = entity['Animal']

        self.D.entity_creator.morth_target_to(entity, animal.adult_name)
        self.create_children(entity)

        print(f"{animal.baby_name} (id:{entity['id']}) вырос и стал {animal.adult_name}")

    def create_children(self, entity):
        pos = entity['Position']
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        shuffle(directions)

        for dx, dy in directions:

            if Movement._can_move_to(pos.x + dx, pos.y + dy, self.D.entities, self.D.map):
                (x, y) = (pos.x + dx, pos.y + dy)

                child_name = entity['Animal'].baby_name
                child_template = self.D.entity_creator.create_entity(child_name, x, y)
                self.D.entity_manager.save_spawn_add(child_template)
                return
            
        print("Не удалось заспавнить ребёнка")