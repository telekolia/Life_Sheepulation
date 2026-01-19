from systems.component_class import Component

from random import randint

class Plant(Component):
    def __init__(self, growth_time, growth_stage_texture_names, is_mature=False):
        self.is_mature = is_mature
        self.growth_stage = 0
        self.growth_time = growth_time
        self.growth_stage_texture_names = [row[:] for row in growth_stage_texture_names]


class GrowthSystem:
    @staticmethod
    def update(entities):
        for entity in entities.values():
            if 'Plant' in entity:
                id = entity['id']
                renderable = entity['Renderable']
                plant = entity['Plant']
                stage_duration = plant.growth_time / (len(plant.growth_stage_texture_names) - 1)

                if not plant.is_mature:
                    plant.growth_stage += randint(1, 3)
                    current_stage = int(plant.growth_stage // stage_duration)
                    renderable.texture_name = plant.growth_stage_texture_names[current_stage]
                    if plant.growth_stage >= plant.growth_time:
                        plant.is_mature = True
                        # print(f"Куст {id} дал ягоды!")
