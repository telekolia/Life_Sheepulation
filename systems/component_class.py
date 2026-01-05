from abc import ABC
import copy

class Component(ABC):
    def clone(self, **kwargs):
        new_instance = self.__class__.__new__(self.__class__)
        
        for key, value in self.__dict__.items():
            if isinstance(value, (list, dict)):
                setattr(new_instance, key, copy.deepcopy(value))
            else:
                setattr(new_instance, key, value)
        
        for key, value in kwargs.items():
            if hasattr(new_instance, key):
                setattr(new_instance, key, value)
        
        return new_instance
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)