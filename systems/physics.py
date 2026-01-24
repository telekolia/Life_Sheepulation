# Consept

# from component_class import Component
# from position import Position

# class PhysicComponent(Component):
#     def __init__(self, velosity: Position, mass):
#         self.velosity = velosity
#         self.mass = mass

# class PhysicSystem:
#     def __init__(self, entity_manager):
#         self.entity_manager = entity_manager

#     def update(self):
#         for entity in self.entity_manager.entities.values():
#             self.update_position(entity)

#     def update_position(self, entity):
#             if 'Position' in entity:
#                 phys = entity['PhysicComponent']
#                 pos = entity['Position']

#                 pos.x += phys.velosity.x
#                 pos.y += phys.velosity.y
    