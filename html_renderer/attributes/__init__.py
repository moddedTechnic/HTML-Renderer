from typing import NewType, Union

from ..selector import Selectable

Attribute = NewType('Attribute', Selectable)
class Attribute(Selectable):
    'Generic attribute, is the base class for all attributes'

    type: str = None
    ''' The type of attribute, used to produce the attribute string for tags
    If left as ``None``, gets set to the class name, in lowercase
    '''

    def __init__(self) -> None:
        if not self.type: self.type = self.__class__.__name__.lower()
        self.value: str = ''

    def __bool__(self) -> bool: return bool(self.value)
    def __repr__(self) -> str: return self.__class__.__name__ + '(\'' + abs(self) + '\')'
    def __str__(self) -> str: return self.type + '="' + abs(self) + '"'

    def __eq__(self, other: Union[str, Attribute]) -> bool:
        if isinstance(other, Attribute): return self.type == other.type and self.value == other.value
        if isinstance(other, str): return self.value == other
        return NotImplemented

    def __ne__(self, other: Union[str, Attribute]) -> bool:
        if isinstance(other, Attribute):
            return self.type != other.type or self.value != other.value
        if isinstance(other, str): return self.value != other
        return NotImplemented

    def __abs__(self) -> str: return self.value


from .class_ import *
from .id import *

Attributes = NewType('Attributes', Selectable)
class Attributes(Selectable):
    def __init__(self) -> None:
        self.cls = Class()
        self.id = Id()

    def __add__(self, other: Union[Class]) -> Attributes:
        if isinstance(other, (Class, Id,)):
            a = Attributes()
            a += other
            return a

    def __iadd__(self, other: Union[Class]) -> Attributes:
        if isinstance(other, Class): self.cls += other
        elif isinstance(other, Id): self.id.value = other.value
        elif isinstance(other, Attribute):
            try:
                self[other.type] += other
            except TypeError:
                self[other.type] = other
        else: return NotImplemented
        return self

    def __iter__(self):
        yield self.cls
        yield self.id
