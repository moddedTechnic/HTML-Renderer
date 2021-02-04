from . import Tag

class P(Tag): pass

class A(Tag): pass
class BB(Tag): pass

class Abbr(Tag): pass
class Acronym(Tag): type = 'abbr'
class Address(Tag): pass

class B(Tag): pass
class I(Tag): pass
class S(Tag): pass
class U(Tag): pass

class Em(Tag): pass
class Big(Tag): pass
class Center(Tag): pass
class Small(Tag): pass
class Strike(Tag): pass
class Strong(Tag): pass

class BlockQuote(Tag): pass
class Q(Tag): pass

class Cite(Tag): pass
class Dfn(Tag): pass

class DD(Tag): pass
class DL(Tag): pass
class DT(Tag): pass
class LI(Tag): pass
class OL(Tag): pass
class UL(Tag): pass

class Dir(Tag): type = 'ul'
class Menu(Tag): pass
class MenuItem(Tag): pass

class Del(Tag): pass
class Ins(Tag): pass
class Mark(Tag): pass

class Sub(Tag): pass
class Sup(Tag): pass

class Title(Tag): pass

class BDI(Tag): pass
class BDO(Tag): pass

class Code(Tag): pass
class Output(Tag): pass
class Pre(Tag): pass
class Sample(Tag): pass
class TT(Tag): pass
class Var(Tag): pass

class Dialog(Tag): pass
