from . import Attribute
from typing import Iterable, NewType, Union


Class = NewType('class', Attribute)
class Class(Attribute):
    def __init__(self, classes: Union[str, Iterable[str], Class] = '') -> None:
        super().__init__()
        
        self.value: set[str] = set()
        self += classes

    def __add__(self, other: Union[str, Iterable[str], Class]) -> Class:
        return self.__class__(other)
    def __iadd__(self, other: Union[str, Iterable[str], Class]) -> Class:
        if isinstance(other, str): self.value |= set(s for c in other.split(' ') if (s := c.strip()))
        elif isinstance(other, Class): self.value |= other.value
        elif isinstance(other, Iterable): self.value |= set(other)
        else: return NotImplemented
        return self

    def __abs__(self) -> str: return ' '.join(self.value)

    def __iter__(self) -> Iterable[str]: yield from self.value
    def __next__(self) -> Iterable[str]: return next(self.value)
    def __len__(self) -> Iterable[str]: return len(self.value)

    def __eq__(self, other: Union[str, Iterable[str], Attribute]) -> bool:
        if isinstance(other, str): return self == set(other.split(' '))
        if isinstance(other, Iterable): return self.value == set(other)
        if isinstance(other, Class): return self.value == other.value
        return super().__eq__(other)

    def __ne__(self, other: Union[str, Iterable[str], Class]) -> bool:
        if isinstance(other, str): return self != set(other.split(' '))
        if isinstance(other, Iterable): return sorted(list(other)) != sorted(list(self.value))
        if isinstance(other, Class): return self != other.value
        return super().__ne__(other)

    def __contains__(self, other: Union[str, Iterable[str], Class]) -> bool:
        if isinstance(other, str): return other in self.value
        if isinstance(other, Iterable): return len(self.value & set(other)) > 0
        if isinstance(other, Class): return other.value in self
        return NotImplemented

    def __selector__(self) -> str:
        return ''.join(f'.{c}' for c in self.value)
