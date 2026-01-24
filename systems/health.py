from systems.component_class import Component

class Health(Component):
    def __init__(self, current_hp, max_hp, death_texture_name, is_alive = True):
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.is_alive = is_alive
        self.death_texture_name = death_texture_name

class HealthSystem():
    def __init__(self, D):
        self.D = D

    def update(self):
        for entity in self.D.entities.values():
            if 'Health' in entity and 'Renderable' in entity:
                if entity['Health'].current_hp <= 0.0 and entity['Health'].is_alive:
                    entity['Health'].is_alive = False
                    entity['Renderable'].texture_name = entity['Health'].death_texture_name
