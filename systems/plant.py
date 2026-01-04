import random

class Plant():
    def __init__(self, growrh_time, growth_stage_texture_names, is_mature=False):
        self.is_mature = is_mature
        self.growth_stage = 0
        self.growth_time = growrh_time
        self.growth_stage_texture_names = [row[:] for row in growth_stage_texture_names]

    # @staticmethod
    # def clone(source, **kwargs):
    #     if 'Plant' in source:
    #         if 'src_type' in kwargs:
    #             if kwargs['src_type'] == 'entity':
    #                 plant_data = source['Plant']
    #                 return Plant(plant_data.growth_time, plant_data.growth_stage_texture_names, plant_data.is_mature)
    #             elif kwargs['src_type'] == 'dictionary':
    #                 plant = source['Plant']
    #                 return Plant(plant['growth_time'], plant['growth_stage_texture_names'])

class GrowthSystem:
    @staticmethod
    def update(entities):
        for entity in entities:
            if 'Plant' in entity:
                id = entity['id']
                renderable = entity['Renderable']
                plant = entity['Plant']
                stage_duration = plant.growth_time / (len(plant.growth_stage_texture_names) - 1)

                if not plant.is_mature:
                    plant.growth_stage += random.randint(1, 3)
                    current_stage = int(plant.growth_stage // stage_duration)
                    renderable.texture_name = plant.growth_stage_texture_names[current_stage]
                    if plant.growth_stage >= plant.growth_time:
                        plant.is_mature = True
                        # print(f"Куст {id} дал ягоды!")
