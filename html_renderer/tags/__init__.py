from ..tag import Tag, Text
from .default import *

def get_tag(tag_name: str, default=Tag) -> type:
    return {
        name.lower(): tag 
    for name, tag in globals().items()
    if isinstance(tag, type) and issubclass(tag, Tag) }.get(tag_name, default)
