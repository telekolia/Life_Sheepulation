class HealthSystem():
    @staticmethod
    def update(entities):
        for entity in entities:
            if 'Health' in entity and 'Renderable' in entity:
                if entity['Health'].current_hp <= 0 and entity['Health'].is_alive:
                    entity['Health'].is_alive = False
                    entity['Renderable'].texture_name = entity['Health'].death_texture_name
