import json
from systems.__init__ import *
from pathlib import Path
import random

class EntityManager():
    total_entities_ever_existed = 0
    entity_types = {}
    entities = {}

    @classmethod
    def load_directory(self, directory_path, recursive = True):
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
                    EntityManager.entity_types[entity_name] = EntityManager._execute_entity_from_json(entity_data)
                    print(f"Loaded entity: {entity_name}")

            except Exception as e:
                print(f"[Х] Load falue {entity_name}: {e}")

        print(f"Total entities loaded: {len(EntityManager.entity_types)}")
    
    @classmethod
    def update(self, map):
        HealthSystem.update(EntityManager.entities)
        HungerSystem.update(EntityManager.entities)
        AnimalSystem.update(EntityManager.entities, map)
        GrowthSystem.update(EntityManager.entities)

    @classmethod
    def draw(self, window):
        RenderSystem.draw(window, EntityManager.entities)

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

        return entity

    @classmethod
    def batch_spawn(self, map, entity_name, count):
        generated = 0
        map_size = len(map)

        while generated < count:
            x = random.randint(0, map_size - 1)
            y = random.randint(0, map_size - 1)

            tile = map[x][y]
            if tile.type == "g":  # Только на траве
                # Проверяем, нет ли уже сущности в этой клетке
                occupied = False

                for entity in EntityManager.entities.values():
                    if ('Position' in entity and
                        entity['Position'].x == x and
                        entity['Position'].y == y and
                        entity.get('type') in ['sheep', 'bush']):
                        occupied = True
                        break

                if not occupied:
                    self.spawn_entity(entity_name, x, y)
                    generated += 1

    @classmethod
    def spawn_entity(self, entity_name, x, y):
        entity = (self.create_entity(entity_name, x, y)).copy()

        type = entity['type']
        EntityManager.total_entities_ever_existed += 1
        entity['id'] = EntityManager.total_entities_ever_existed

        EntityManager.entities[entity['id']] = entity
        print(f"Entity {entity['id']} spawned in position ({entity['Position'].x}, {entity['Position'].y})")

    @classmethod
    def create_entity(self, entity_name, x = 0, y = 0):
        if entity_name not in EntityManager.entity_types:
            raise ValueError(f"Entity '{entity_name}' not found")

        template = EntityManager.entity_types[entity_name]
        new_entity = EntityManager._create_entity_from_template(template, x, y)

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

        return entity
