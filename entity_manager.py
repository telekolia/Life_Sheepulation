import json
from systems.__init__ import *
from pathlib import Path
import random

components = {'Position': Position,
              'Renderable': Renderable,
              'Plant': Plant,
              'Health': Health,
              'Hunger': Hunger,
              'Animal': Animal,
              'Tile': Tile,
              'Age': Age,
}

simple_components = ['id', 'type', 'state', 'target_id']

class EntityLoader:
    @staticmethod
    def load_directory(entity_types, directory_path, recursive = True):
        path = Path(directory_path)

        if recursive:
            files = path.rglob("*.json")
        else:
            files = path.glob("*.json")

        for file_path in files:
            entity_name = file_path.stem
            try:
                with open(str(file_path), 'r', encoding='utf-8') as f:
                    entity_data = json.load(f)
                    entity_types[entity_name] = EntityLoader._execute_entity_from_json(entity_data)
                    print(f"Loaded entity: {entity_name}")

            except Exception as e:
                print(f"[Х] Load falue {entity_name}: {e}")

        print(f"Total entities loaded: {len(entity_types)}")

    @staticmethod
    def _execute_entity_from_json(entity_data):
        entity = {}
        
        for simple_component in simple_components:
            if simple_component in entity_data:
                entity[simple_component] = entity_data[simple_component]
        
        for component_name, component in components.items():
            if component_name in entity_data:
                entity[component_name] = component.from_dict(entity_data[component_name])

        return entity

class EntityCreator:
    entity_types = {}

    @classmethod
    def create_entity(cls, entity_name, x = 0, y = 0):
        if entity_name not in EntityCreator.entity_types:
            raise ValueError(f"Entity '{entity_name}' not found")

        template = EntityCreator.entity_types[entity_name]
        new_entity = EntityCreator._create_entity_from_template(template, x, y)

        return new_entity

    @staticmethod
    def _create_entity_from_template(template, x, y):
        entity = {}

        for simple_component in simple_components:
            if simple_component in template:
                entity[simple_component] = template[simple_component]
        
        for component_name, component in components.items():
            if component_name in template:
                entity[component_name] = component.clone(template[component_name])

        if 'Position' in entity:
            entity['Position'].x = x
            entity['Position'].y = y

        return entity

class EntityManager:
    def __init__(self):
        self.total_entities_ever_existed = 0
        self.entities = {}
        self.map = None

    def set_map(self, map):
        self.map = map

    def generate_default_entities(self):
        self.batch_spawn("hyena", 2)
        self.batch_spawn("sheep", 3)
        self.batch_spawn("bush", 10)

    def update(self):
        HealthSystem.update(self.entities)
        HungerSystem.update(self.entities)
        AnimalSystem.update(self.entities, self.map)
        GrowthSystem.update(self.entities)
        AgeSystem.update(self.entities)
        
        self._delete_destroed_entities()

    @staticmethod
    def is_entity_deleted(entity):
        return entity['id'] == 0

    @staticmethod
    def delete_this_entity(entity):
        entity['id'] = 0

    def _delete_destroed_entities(self):
        destroed_entity_ids = []
        for id, entity in self.entities.items():
            if entity['id'] == 0:
                destroed_entity_ids.append(id)

        for id in destroed_entity_ids:
            del self.entities[id]

    def draw(self, window):
        RenderSystem.draw(window, self.entities)

    def batch_spawn(self, entity_name, count):
        generated = 0
        map_size = len(self.map)

        while generated < count:
            x = random.randint(0, map_size - 1)
            y = random.randint(0, map_size - 1)

            tile = self.map[x][y]
            if tile["Tile"].is_passable:  # Только на траве
                # Проверяем, нет ли уже сущности в этой клетке
                occupied = False

                for entity in self.entities.values():
                    if ('Position' in entity and
                        entity['Position'].x == x and
                        entity['Position'].y == y and
                        entity.get('type') in ['sheep', 'bush']):
                        occupied = True
                        break

                if not occupied:
                    self.spawn(entity_name, x, y)
                    generated += 1

    def spawn(self, entity_name, x, y):
        entity = (EntityCreator.create_entity(entity_name, x, y)).copy()
        self.add(entity)

    def add(self, entity):
        self.total_entities_ever_existed += 1
        entity['id'] = self.total_entities_ever_existed

        self.entities[entity['id']] = entity
        print(f"Entity {entity['id']} spawned in position ({entity['Position'].x}, {entity['Position'].y})")
