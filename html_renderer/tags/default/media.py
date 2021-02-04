from . import Tag

class Audio(Tag): pass
class Img(Tag): pass
class Map(Tag): pass
class Picture(Tag): pass
class Source(Tag): pass
class SVG(Tag): pass
class Track(Tag): pass
class Video(Tag): pass

# Inteded for Flash (override?)
class Applet(Tag): type = 'object'
class Embed(Tag): pass

# Flash, web pages, applets, PDFs
class Object(Tag): pass
class Param(Tag): pass

class Canvas(Tag): pass
class Frame(Tag): pass
class FrameSet(Tag): pass
class IFrame(Tag): pass

class Link(Tag): pass
class Meta(Tag): pass
class NoScript(Tag): pass
class Script(Tag): pass
class Style(Tag): pass

class Base(Tag): pass
class BaseFont(Tag): pass
class Font(Tag): pass
