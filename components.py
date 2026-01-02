class Position():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Renderable():
    def __init__(self, texture_name, layer = 0):
        self.texture_name = texture_name
        self.layer = layer


class Plant():
    def __init__(self, growrh_time, growth_stage_texture_names, is_mature=False):
        self.is_mature = is_mature
        self.growth_stage = 0
        self.growth_time = growrh_time
        self.growth_stage_texture_names = [row[:] for row in growth_stage_texture_names]

class Health():
    def __init__(self, current_hp, max_hp, death_texture_name, is_alive = True):
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.is_alive = is_alive
        self.death_texture_name = death_texture_name


class Hunger():
    def __init__(self, current_satiety, max_satiety):
        self.current_satiety = current_satiety
        self.max_satiety = max_satiety


class Animal():
    def __init__(self, type, max_amount_of_children, adult_texture_name, baby_texture_name):
        self.type = type
        self.max_amount_of_children = max_amount_of_children
        self.adult_texture_name = adult_texture_name
        self.baby_texture_name = baby_texture_name
