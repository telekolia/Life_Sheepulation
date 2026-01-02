class HungerSystem():
    @staticmethod
    def update(entities):
        for entity in entities:
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
