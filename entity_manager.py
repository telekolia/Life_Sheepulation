import json
from components import Position, Renderable, Health, Plant, Hunger, Animal
from pathlib import Path
import random

class EntityManager():
    def __init__(self):
        self.entity_types = {}

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
                    self.entity_types[entity_name] = EntityManager._execute_entity_from_json(entity_data)
                    print(f"Loaded entity: {entity_name}")

            except Exception as e:
                print(f"[Х] Load falue {entity_name}: {e}")

        print(f"Total entities loaded: {len(self.entity_types)}")
        return self.entity_types

    @staticmethod
    def _execute_entity_from_json(entity_data):
        entity = {}

        if "id" in entity_data:
            entity['id'] = entity_data['id']
        if "type" in entity_data:
            entity['type'] = entity_data['type']
        if "Position" in entity_data:
            pos = entity_data['Position']
            entity['Position'] = Position(pos['x'], pos['y'])
        if "Renderable" in entity_data:
            renderable = entity_data['Renderable']
            entity['Renderable'] = Renderable(renderable['texture_name'], renderable['layer'])
        if "Health" in entity_data:
            health = entity_data['Health']
            entity['Health'] = Health(health['current_hp'], health['max_hp'], health['death_texture_name'])
        if "Plant" in entity_data:
            plant = entity_data['Plant']
            entity['Plant'] = Plant(plant['growth_time'], plant['growth_stage_texture_names'])
        if "Hunger" in entity_data:
            hunger = entity_data['Hunger']
            entity['Hunger'] = Hunger(hunger['current_satiety'], hunger['max_satiety'])
        if "Animal" in entity_data:
            animal = entity_data['Animal']
            entity['Animal'] = Animal(animal['type'], animal['max_amount_of_children'],
                                      animal['adult_texture_name'], animal['baby_texture_name'])
        if "target_id" in entity_data:
            entity['target_id'] = entity_data['target_id']
        if "state" in entity_data:
            entity['state'] = entity_data['state']

        return entity

    def batch_spawn(self, entities, map, entity_name, count):
        generated = 0
        map_size = len(map)

        while generated < count:
            x = random.randint(0, map_size - 1)
            y = random.randint(0, map_size - 1)

            tile = map[x][y]
            if tile.type == "g":  # Только на траве
                # Проверяем, нет ли уже сущности в этой клетке
                occupied = False

                for entity in entities:
                    if ('Position' in entity and
                        entity['Position'].x == x and
                        entity['Position'].y == y and
                        entity.get('type') in ['sheep', 'bush']):
                        occupied = True
                        break

                if not occupied:
                    self.spawn_entity(entities, entity_name, x, y)
                    generated += 1

    def spawn_entity(self, entities, entity_name, x, y):
        entity = (self.create_entity(entity_name, x, y)).copy()

        type = entity['type']
        entity['id'] = f"{type}_{len(entities)}"

        entities.append(entity)
        print(f"Entity {entity['id']} spawned in position ({entity['Position'].x}, {entity['Position'].y})")

    def create_entity(self, entity_name, x = 0, y = 0):
        if entity_name not in self.entity_types:
            raise ValueError(f"Entity '{entity_name}' not found")

        template = self.entity_types[entity_name]
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
            render_data = template['Renderable']
            entity['Renderable'] = Renderable(render_data.texture_name, render_data.layer)

        if 'Health' in template:
            health_data = template['Health']
            entity['Health'] = Health(health_data.current_hp, health_data.max_hp,
                                      health_data.death_texture_name, health_data.is_alive)

        if 'Hunger' in template:
            hunger_data = template['Hunger']
            entity['Hunger'] = Hunger(hunger_data.current_satiety, hunger_data.max_satiety)

        if 'Plant' in template:
            plant_data = template['Plant']
            entity['Plant'] = Plant(plant_data.growth_time, plant_data.growth_stage_texture_names, plant_data.is_mature)

        if 'Animal' in template:
            animal_data = template['Animal']
            entity['Animal'] = Animal(animal_data.type, animal_data.max_amount_of_children,
                                      animal_data.adult_texture_name, animal_data.baby_texture_name)

        return entity
