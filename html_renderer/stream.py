from typing import Any, Optional

class Stream:
    def __init__(self):
        self.data = []

    def __iter__(self): return iter(self.data)
    def __next__(self): return next(self.data)
    def __repr__(self) -> str: return f'{self.__class__.__qualname__}:' + '\n\t'.join(self.data)

    def write(self, s: Any): self.data.append(s)
    def read(self, sep: Optional[str] = '\n'): return sep.join(self.data)

    @staticmethod
    def flush(): pass

    def print(self): print(self.read())

