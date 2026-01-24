from systems.component_class import Component

class Hunger(Component):
    def __init__(self, current_satiety, max_satiety):
        self.current_satiety = current_satiety
        self.max_satiety = max_satiety

class HungerSystem():
    def __init__(self, D):
        self.D = D

    def proccess(self):
        for entity in self.D.entities.values():
            if 'Hunger' in entity:
                hunger = entity['Hunger']
                if hunger.current_satiety > 0.0:
                    if 'Health' in entity:
                        health = entity['Health']
                        if health.is_alive:
                            if health.current_hp < health.max_hp and hunger.current_satiety > hunger.max_satiety // 2:
                                delta_hp = health.max_hp - health.current_hp
                                if delta_hp < 0.1:
                                    health.current_hp += delta_hp
                                    hunger.current_satiety -= delta_hp * 2
                                else:
                                    health.current_hp += 0.1
                                    hunger.current_satiety -= 0.2
                    hunger.current_satiety -= 0.5
                else:
                    if 'Health' in entity:
                        if 'Health' in entity:
                            health = entity['Health']
                            if health.is_alive:
                                health.current_hp -= 0.25
