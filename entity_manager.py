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
    def _create_entity_from_template(template, x=0, y=0):
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
    
    @staticmethod
    def morth_target_to(morthing_target, entity_name):
        template = EntityCreator.entity_types[entity_name]

        morthing_target['type'] = template['type']

        conserved_components = ['Age', 'Health', 'Hunger', 'Position']

        for component_name, component in components.items():
            if component_name in template and (component_name not in conserved_components or component_name not in morthing_target):
                morthing_target[component_name] = component.clone(template[component_name])
        
        if 'Health' in template and 'Health' in morthing_target:
                morthing_target['Health'].death_texture_name = template['Health'].death_texture_name

        # for component_name in morthing_target.keys():
        #     if component_name not in template:
        #         del morthing_target[component_name]

class EntityManager:
    def __init__(self):
        self.total_entities_ever_existed = 0
        self.entities = {}
        self.map_size = 10
        self.map = [[None for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.entities_to_spawn = []
        self.generate_default_map()

        self.generate_default_entities()
        
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
                    self.init_spawn("water_tile", x, y)
                else:
                    self.init_spawn("grass_tile", x, y)

        for entity in self.entities.values():
            if "Tile" in entity and "Position" in entity:
                pos = entity["Position"]
                self.map[pos.x][pos.y] = entity
                # print(f"получилось {pos.x},{pos.y}")
                

    def generate_default_entities(self):
        self.batch_spawn("hyena", 2)
        # self.batch_spawn("sheep", 2)
        self.batch_spawn("bush", 4)
        self.batch_spawn("baby_sheep", 2)

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
                    self.init_spawn(entity_name, x, y)
                    generated += 1

    def init_spawn(self, entity_name, x, y):
        entity = EntityCreator.create_entity(entity_name, x, y)
        self.add(entity)

    def save_spawn_add(self, entity):
        new_entity_template = entity
        self.entities_to_spawn.append(new_entity_template)

    def save_spawn_proccess(self):
        for entity in self.entities_to_spawn:
            new_entity = EntityCreator._create_entity_from_template(entity)
            self.add(entity)
        
        self.entities_to_spawn.clear()

    def add(self, entity):
        self.total_entities_ever_existed += 1
        entity['id'] = self.total_entities_ever_existed

        self.entities[entity['id']] = entity
        print(f"Entity {entity['id']} spawned in position ({entity['Position'].x}, {entity['Position'].y})")

class EntityMailman:
    def __init__(self, entity_manager, entity_creator):
        self.entity_manager = entity_manager
        self.entity_creator = entity_creator

    def add_entity_to_safe_spawn(self):
        pass