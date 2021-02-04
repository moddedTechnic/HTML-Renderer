from typing import Union

NotImplementedType = type(NotImplemented)


class Selectable:
    def __selector__(self) -> Union[str, NotImplementedType]:
        return NotImplemented


def selector(x: Selectable):
    return x.__selector__()
