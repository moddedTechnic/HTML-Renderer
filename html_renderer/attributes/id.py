from . import Attribute


class Id(Attribute):
    def __selector__(self) -> str:
        return '#' + self.value
