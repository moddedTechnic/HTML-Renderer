from typing import Iterable, NewType, Union
from xml.etree.ElementTree import Comment, Element, tostring
from .stream import Stream
import sys

Tag = NewType('Tag', object)

BLANK_ATTR = '{%blank-attr%}'

def _blank_container():
    return Element('div', {'style': 'display: inline;'})

class Tag:
    type: str = None
    is_startend: bool = False
    classes: list[str] = []

    def __init__(self, *, attrs: dict = None):
        self.attrs: dict[str, str] = attrs or {}
        if 'class' in attrs:
            if isinstance(attrs['class'], str):
                attrs['class'] = attrs['class'].split(' ')
        else:
            attrs['class'] = []

        self.children: list[Tag] = []

        if not self.type: self.type = self.__class__.__name__.lower()

    def __str__(self) -> str: return tostring(self.to_tree(), encoding='unicode', method='html').replace(f'="{BLANK_ATTR}"', '')
        
    def __repr__(self) -> str: return f'{self.__class__.__qualname__}(attrs={{{self.attr_strings(", ")}}}, children=[{", ".join(repr(child) for child in self.children)}])'

    def __getitem__(self, idx: Union[int, str]):
        if isinstance(idx, int):
            return self.children[int]
        elif isinstance(idx, str):
            return self.attrs[idx]
        else:
            raise TypeError(f'Expected idx to be str or int (got {idx.__class__.__name__})')

    def __iter__(self) -> Iterable[Tag]: return iter(self.children)
    def __next__(self) -> Tag: return next(self.children)
    def __len__(self) -> int: return len(self.children)

    def __iadd__(self, other: Union[Tag, str]) -> Tag:
        if isinstance(other, str): self.add_class(other)
        elif isinstance(other, Tag): self.add_child(other)
        return self

    def to_tree(self):
        this = Element(self.type, self.serializable_attrs())
        for child in self.children:
            this.append(child.to_tree())
        if not self.is_startend and not self.children:
            this.append(Comment(' '))
        return this

    def attr_strings(self, delim: str = ' ') -> str:
        attrs = []
        for k, v in self.attrs.items():
            if k == 'class': attrs.append('class="' + ' '.join(v) + '"') if v else None
            elif v is None: attrs.append(k)
            else: attrs.append(f'{k}="{v}"')
        return delim.join(attrs)

    def serializable_attrs(self):
        attrs = {}
        for k, v in self.attrs.items():
            if k == 'class': attrs[k] = ' '.join(v) if v else ''
            else: attrs[k] = BLANK_ATTR if v is None else v
        return attrs

    def print(self, indent=0, end=''):
        print('    ' * indent + f'{self.__class__.__qualname__}(')
        indent += 1
        if len(self.attrs.values()):
            print('    ' * indent + 'attrs={')
            indent += 1
            for attr in self.attr_strings(',\n').split('\n'):
                print('    ' * indent + attr)
            indent -= 1
            print('    ' * indent + '},')
        else: print('    ' * indent + 'attrs={},')

        if len(self.children):
            print('    ' * indent + 'children=[')
            indent += 1
            for child in self.children:
                child.print(indent, ',')
            indent -= 1
            print('    ' * indent + ']')
        else: print('    ' * indent + 'children=[]')
        indent -= 1
        print('    ' * indent + ')' + end)

    def add_child(self, child: Tag):
        self.children.append(child)

    def add_class(self, cls: str):
        if 'class' not in self.attrs: self.attrs['class'] = []
        self.attrs['class'].append(cls)

class Text:
    def __init__(self, content: str = ''):
        self.content = content

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return self.__class__.__name__ + f'(content=\'{self.content}\')'

    def to_tree(self):
        stem = _blank_container()
        stem.text = self.content
        return stem

    def print(self, indent=0, end='') -> str:
        print('    ' * indent + repr(self) + end)
