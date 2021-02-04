from collections import deque
from html.parser import HTMLParser
from os.path import join
from typing import Optional, Union

from .tag import Tag, Text
from .tags.default.block import Div

from . import TEMPLATES_PATH
from .tags import get_tag


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tag_stack: deque[Tag] = deque()
        self.result: Union[Tag, None] = None

    def handle_starttag(self, tag_name: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = get_tag(tag_name, default=Div)(attrs=dict(attrs, tagtype=tag_name))
        self.tag_stack.append(tag)

    def handle_endtag(self, tag_name: str) -> None:
        tag = self.tag_stack.pop()
        if self.tag_stack:
            self.tag_stack[-1].add_child(tag)
        else: self.result = tag

    def handle_startendtag(self, tag_name: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = get_tag(tag_name, Div)(attrs=dict(attrs, tagtype=tag_name))
        if self.tag_stack:
            self.tag_stack[-1].add_child(tag)
        self.result = tag

    def handle_data(self, data: str) -> None:
        if self.tag_stack and data.strip():
            self.tag_stack[-1].add_child(Text(content=data))

    def parse(self, *filename):
        with open(join(TEMPLATES_PATH, *filename), 'r') as f:
            data = f.read()
        self.parse_text(data)
    parse_text = HTMLParser.feed
