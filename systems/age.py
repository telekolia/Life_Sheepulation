from systems.component_class import Component

class Age(Component):
    day_latensy = 2 # in tics
    days_in_year = 365

    def __init__(self, time, day, year):
        self.time = time
        self.day = day
        self.year = year
    
    def update(self):
        self.time += 1

        if self.time >= Age.day_latensy:
            self.time = 0
            self.day += 1

        if self.day >= Age.days_in_year:
            self.day = 0
            self.year += 1

class AgeSystem:
    @staticmethod
    def update(entities):
        for entity in entities.values():
            if 'Age' in entity and 'Health' in entity and entity['Health'].is_alive:
                entity['Age'].update()
