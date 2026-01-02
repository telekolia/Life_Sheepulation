import random

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
