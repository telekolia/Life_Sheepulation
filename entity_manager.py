import json
from systems.__init__ import *
from pathlib import Path
import random

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
        
        if "id" in entity_data:
            entity['id'] = entity_data['id']
        if "type" in entity_data:
            entity['type'] = entity_data['type']
        if "target_id" in entity_data:
            entity['target_id'] = entity_data['target_id']
        if "state" in entity_data:
            entity['state'] = entity_data['state']
        
        if "Position" in entity_data:
            entity['Position'] = Position.from_dict(entity_data['Position'])
        if "Renderable" in entity_data:
            entity['Renderable'] = Renderable.from_dict(entity_data['Renderable'])
        if "Health" in entity_data:
            entity['Health'] = Health.from_dict(entity_data['Health'])
        if "Plant" in entity_data:
            entity['Plant'] = Plant.from_dict(entity_data['Plant'])
        if "Hunger" in entity_data:
            entity['Hunger'] = Hunger.from_dict(entity_data['Hunger'])
        if "Animal" in entity_data:
            entity['Animal'] = Animal.from_dict(entity_data['Animal'])
        if "Tile" in entity_data:
            entity['Tile'] = Tile.from_dict(entity_data['Tile'])

        return entity

class EntityManager():
    def __init__(self):
        self.total_entities_ever_existed = 0
        self.entity_types = {}
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
                    self.spawn_entity(entity_name, x, y)
                    generated += 1

    def spawn_entity(self, entity_name, x, y):
        entity = (self.create_entity(entity_name, x, y)).copy()

        self.total_entities_ever_existed += 1
        entity['id'] = self.total_entities_ever_existed

        self.entities[entity['id']] = entity
        print(f"Entity {entity['id']} spawned in position ({entity['Position'].x}, {entity['Position'].y})")

    def create_entity(self, entity_name, x = 0, y = 0):
        if entity_name not in self.entity_types:
            raise ValueError(f"Entity '{entity_name}' not found")

        template = self.entity_types[entity_name]
        new_entity = self._create_entity_from_template(template, x, y)

        return new_entity

    @staticmethod
    def _create_entity_from_template(template, x, y):
        entity = {}

        for key, value in template.items():
            if key in ['id', 'type', 'state', 'target_id']:
                entity[key] = value

        if 'Position' in template:
            entity['Position'] = Position(x, y)

        if 'Renderable' in template:
            entity['Renderable'] = Renderable.clone(template['Renderable'])

        if 'Health' in template:
            entity['Health'] = Health.clone(template['Health'])

        if 'Hunger' in template:
            entity['Hunger'] = Hunger.clone(template['Hunger'])

        if 'Plant' in template:
            entity['Plant'] = Plant.clone(template['Plant'])

        if 'Animal' in template:
            entity['Animal'] = Animal.clone(template['Animal'])

        if 'Tile' in template:
            entity['Tile'] = Tile.clone(template['Tile'])

        return entity
