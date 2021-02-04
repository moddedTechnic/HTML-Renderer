import sys
from collections import defaultdict
from functools import wraps
from html.parser import HTMLParser
from itertools import chain
from os.path import join
from queue import LifoQueue as Queue
from typing import Callable, Iterable, NewType, Optional
from re import sub, compile as re_compile, escape as re_escape

from .. import (HTDOCS_PATH, Environment, export, get_parameters, load_charrefs,
               log)


class ContextItem:
    def __init__(self, k='', v=''):
        self.raw_k = k
        self.k = k
        self.raw_v = v
        self.v = v

    @property
    def k(self):
        return self.search

    @k.setter
    def k(self, k):
        self.search = re_compile(f'\\{{\\{{ *{k} *\\}}\\}}')

    @property
    def v(self):
        return self.value

    @v.setter
    def v(self, v):
        self.value = re_escape(v)


strs = Iterable[str]
map_strstr = dict[str, str]
Context = NewType('Context', defaultdict[str, ContextItem])
_TagRenderer = NewType('_TagRenderer', object)
_tag_end_func = Callable[[_TagRenderer], str]


class _RenderStream:
    def __init__(self):
        self.data = []

    def __iter__(self):
        return self.data

    def __next__(self):
        return next(self.data)

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}:' + '\n\t'.join(self.data)

    def write(self, s):
        self.data.append(s)

    def read(self):
        return '\n'.join(self.data)

    def flush(self):
        log('Flushed', self)

    def print(self):
        print(self.read())


class _RendererBase(HTMLParser):
    def __init__(self, context: Optional[Context] = None, blocks=None) -> None:
        super().__init__(convert_charrefs=False)
        self.context: Context = context or self.default_context()
        for k, v in self.context.items():
            if isinstance(v, ContextItem): v = v.raw_v
            self.context[k] = ContextItem(k, v.replace('%20', ' ').replace('%27', '\''))
        self.accordions = []
        self.blocks = blocks or defaultdict(_RenderStream)
        self.block_names = []
        self.charrefs = load_charrefs()
        self.codes = None
        self.extends = Queue()

    def handle_startendtag(self, tagname: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attrs = dict(attrs)
        handler = '_handle_' + tagname.replace('-', '_')
        if hasattr(self, handler):
            handler_func = getattr(self, handler)
            if isinstance(handler_func, Iterable):
                tag = ' '.join(f(self, attrs) if '_start' in f.__name__ else f(
                    self) for f in handler_func)
            else:
                tag = handler_func(attrs)
        else:
            tag = self.make_tag_startend(tagname, attrs)
        if tag is not None:
            print(tag)

    def handle_starttag(self, tagname: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attrs = dict(attrs)
        handler = '_handle_' + tagname.replace('-', '_') + '_start'
        if hasattr(self, handler):
            handler_func = getattr(self, handler)
            if isinstance(handler_func, Iterable):
                tag = ' '.join(f(self, attrs) for f in handler_func)
            else:
                tag = handler_func(attrs)
        else:
            tag = self.make_tag_start(tagname, attrs)
        if tag is not None:
            print(tag)

    def handle_endtag(self, tagname: str) -> None:
        handler = '_handle_' + tagname.replace('-', '_') + '_end'
        if hasattr(self, handler):
            handler_func = getattr(self, handler)
            if isinstance(handler_func, Iterable):
                tag = ' '.join(f(self) for f in handler_func)
            else:
                tag = getattr(self, handler)()
        else:
            tag = self.make_tag_end(tagname)
        if tag is not None:
            print(tag)

    def handle_decl(_, decl): return print(f'<!{decl}>')

    def handle_data(self, data: str) -> None:
        if self.codes:
            self.codes['body'].append(data)
        else:
            print(self.populate(data))

    def handle_charref(_, name): return print(f'&#{name};')

    @staticmethod
    def default_context() -> Context:
        return defaultdict(
            ContextItem,
            chain(
                map(
                    lambda x: (x[0], ContextItem(*x)),
                    filter(
                        lambda x: hasattr(x, '__len__') and len(x) == 2,
                        get_parameters(method='GET')
                    )
                ),
                Environment.items()
            )
        )

    def include(self, *, path=None, snippet=None):
        if path:
            self._handle_include({'src': path})
        if snippet:
            self.render_text(snippet)

    def populate(self, data):
        if data and data.strip():
            for ctxt in self.context.values():
                data = sub(ctxt.k, ctxt.v, data)
            for k, v in self.charrefs.items():
                data = sub(k, v, data)
            data = sub(r'\{\{[ a-zA-Z\-_]+\}\}', '', data)
            data = sub(r'\{\&[ a-zA-Z\-_]+\&\}', '', data)
        return data

    @staticmethod
    def add_class(attrs: dict, clsname: str):
        if 'class' in attrs:
            attrs['class'] += ' '
        else:
            attrs['class'] = ''
        attrs['class'] += clsname
        return attrs
        
    def render(self, *filename):
        with open(join(HTDOCS_PATH, *filename), 'r') as f:
            data = f.read()
        self.render_text(data)
    render_text = HTMLParser.feed


class _TagRenderer:
    def make_tag_startend(self, tag: str, attrs: Optional[map_strstr] = None) -> str:
        return f'<{tag} {self.process_attrs(attrs)} />'

    def make_tag_start(self, tag: str, attrs: Optional[map_strstr] = None) -> str:
        return f'<{tag} {self.process_attrs(attrs)}>'

    def make_tag_end(_, tag: str) -> str:
        return f'</{tag}>'
        
    def make_a_start(self, attrs: Optional[map_strstr] = None) -> str:
        if attrs:
            if 'new-tab' in attrs:
                del attrs['new-tab']
                attrs.update(target='_blank')
        return self.make_tag_start('a', attrs)

    def process_attrs(self, attrs: Optional[map_strstr] = None) -> str:
        if attrs:
            return ' '.join(f'{self.populate(k)}="{self.populate(v)}"' for k, v in attrs.items()) if attrs else ''
        else:
            return ''

    def _make_tag_start(func):
        @wraps(func)
        def wrapper(self, attrs, *args, **kwargs):
            return self.make_tag_start(func(*args, **kwargs), attrs)
        return wrapper
    
    def _make_tag_end(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return self.make_tag_end(func(self, *args, **kwargs))
        return wrapper

    @staticmethod
    def get_list_tag(list_type: str) -> str:
        return {
            'definition': 'dl',
            'ordered': 'ol',
            'unordered': 'ul',
            'dl': 'dl',
            'ol': 'ol',
            'ul': 'ul',
        }.get(list_type, '')

    class TagDecorator:
        def __init__(self, tag: str) -> None:
            self.tag = tag

        def __call__(self, func):
            def wrapper(*args, **kwargs):
                return self.decorator(func, *args, **kwargs)
            wrapper.__name__ = self.name
            return wrapper

        @property
        def name(self): return self.tag

        def decorator(*_): return NotImplemented

    class TagStart(TagDecorator):
        def __call__(dec, func):
            def wrapper(*,
                clsnames: Optional[strs] = None,
                compound_clsnames: Optional[strs] = None,
                id: Optional[str] = None
            ):
                @wraps(func)
                def wrapped(self, attrs: map_strstr, *args, **kwargs) -> str:
                    if clsnames:
                        for clsname in clsnames:
                            attrs = self.add_class(attrs, clsname)
                    if compound_clsnames:
                        for clsname in compound_clsnames:
                            try:
                                attrs = self.add_class(attrs, clsname.format(**attrs))
                            except KeyError:
                                continue
                    if id:
                        attrs['id'] = id
                    return func(self, attrs, *args, **kwargs)
                return wrapped
            wrapper.__name__ = dec.name
            return wrapper

        @staticmethod
        def decorator(func, *args1, clsnames, compound_clsnames, id, **kwargs1):
            @wraps(func)
            def wrapper(self, attrs, *args2, **kwargs2):
                if clsnames:
                    for clsname in clsnames:
                        attrs = self.add_class(attrs, clsname)
                if compound_clsnames:
                    for clsname in compound_clsnames:
                        try:
                            attrs = self.add_class(attrs, clsname.format(**attrs))
                        except KeyError:
                            continue
                if id:
                    attrs['id'] = id
                return func(self, attrs, *args1, *args2, **kwargs1, **kwargs2)
            return wrapper

        @property
        def name(self): return self.tag + '_start'

    class TagEnd(TagDecorator):
        @staticmethod
        def decorator(func, *args1, **kwargs1) -> _tag_end_func:
            @wraps(func)
            def wrapped(self, *args2, **kwargs2):
                return func(self, *args1, *args2, **kwargs1, **kwargs2)
            return wrapped
        
        @property
        def name(self): return self.tag + '_end'
            
    class TagStartEnd(TagDecorator):
        @staticmethod
        def decorator(func, *args1, **kwargs1):
            @wraps(func)
            def wrapper(self, attrs, *args2, **kwargs2):
                return func(self, attrs, *args1, *args2, **kwargs1, **kwargs2)
            return wrapper

        @property
        def name(self): return self.tag + '_startend'

    @TagStart('div')
    @_make_tag_start
    def div_start(*_): return 'div'

    @TagEnd('div')
    @_make_tag_end
    def div_end(_): return 'div'

    @TagStart('section')
    @_make_tag_start
    def section_start(*_): return 'section'

    @TagEnd('section')
    @_make_tag_end
    def section_end(_): return 'section'

    @TagStart('a')
    def a_start(self, attrs): return self.make_a_start(attrs)

    @TagEnd('a')
    @_make_tag_end
    def a_end(_): return 'a'

    @TagStart('p')
    @_make_tag_start
    def p_start(*_): return 'p'
        
    @TagEnd('p')
    @_make_tag_end
    def p_end(_): return 'p'

    @TagStart('list')
    @_make_tag_start
    def list_start(self, _, list_type): return self.get_list_tag(list_type)

    @TagEnd('list')
    @_make_tag_end
    def list_end(self, list_type): return self.get_list_tag(list_type)

    @TagStart('ol')
    @_make_tag_start
    def ol_start(*_): return 'ol'

    @TagEnd('ol')
    @_make_tag_end
    def ol_end(_): return 'ol'

    @TagStart('ul')
    @_make_tag_start
    def ul_start(*_): return 'ul'

    @TagEnd('ul')
    @_make_tag_end
    def ul_end(_): return 'ul'

    @TagStart('dl')
    @_make_tag_start
    def dl_start(*_): return 'dl'

    @TagEnd('dl')
    @_make_tag_end
    def dl_end(_): return 'dl'


class _Renderer(_RendererBase, _TagRenderer):
    def __init__(self, context: Optional[Context] = None, blocks=None) -> None:
        super().__init__(context=context, blocks=blocks)
        self.tags = defaultdict(Queue)

    @staticmethod
    def make_attrs(attrs, **defaults):
        _attrs = defaults.copy()
        for from_, to_ in {'cls': 'class', 'initial_scale': 'initial-scale'}.items():
            if from_ in _attrs:
                _attrs[to_] = _attrs[from_]
                del _attrs[from_]
        _attrs.update(attrs)
        return _attrs
    _get_attrs = lambda _, attrs, *attributes, filter=True: {k: attrs.get(
        k) for k in attributes if not filter or attrs.get(k, NameError) != NameError}

    @_TagRenderer.TagStart('codelike')
    def make_codelike_start(self, attrs):
        self.codes = {'attrs': attrs, 'body': []}

    @_TagRenderer.TagEnd('codelike')
    def make_codelike_end(self, tag):
        code, self.codes = self.codes, None
        body = code['body']
        if not body[0].strip():
            body = body[1:]
        return self.make_tag_start(tag, code['attrs']) + self.populate('\n'.join(body)) + self.make_tag_end(tag)

    @_TagRenderer.TagStartEnd('meta')
    def _meta(self, attrs, name):
        return self.make_tag_startend(
            'meta', self.make_attrs(attrs, name=name))

    @_TagRenderer.TagStartEnd('includer')
    def _includer(self, _, path):
        return self.include(path=path)

    def _handle_stylesheet(self, attrs):
        return self.make_tag_startend(
            'link',
            self.make_attrs(attrs, rel='stylesheet',
                            type='text/css', media='all')
        )

    def _handle_extscript(self, attrs):
        return self.make_tag_start(
            'script',
            self.make_attrs(attrs, type='text/javascript')
        ) + self.make_tag_end('script')

    def _handle_favicon(self, attrs):
        return self.make_tag_startend(
            'link',
            self.make_attrs(
                attrs, href='/dashboard/images/favicon.png', rel='icon', type='image/png')
        )

    def _handle_analytics(self, _):
        div = _TagRenderer.div_start(id='fb-root')(self, {}) + _TagRenderer.div_end()(self)
        script = self._handle_extscript(
            {'src': '/dashboard/javascripts/fb_insert.js'})
        return div + script

    _handle_wrapper_start = _TagRenderer.div_start(id='wrapper')
    _handle_wrapper_end = _TagRenderer.div_end()

    _handle_hero_start = _TagRenderer.div_start(clsnames=('hero',))
    _handle_hero_end = _TagRenderer.div_end()

    _handle_row_start = _TagRenderer.div_start(clsnames=('row',))
    _handle_row_end = _TagRenderer.div_end()

    _handle_rows_start = _TagRenderer.div_start(clsnames=('rows',))
    _handle_rows_end = _TagRenderer.div_end()

    _handle_column_start = _TagRenderer.div_start(clsnames=('column',))
    _handle_column_end = _TagRenderer.div_end()

    _handle_columns_start = _TagRenderer.div_start(
        clsnames=('columns',),
        compound_clsnames=('{size}-{count}',)
    )
    _handle_columns_end = _TagRenderer.div_end()

    _handle_literalblock_start = _TagRenderer.div_start(clsnames=('literalblock',))
    _handle_literalblock_end = _TagRenderer.div_end()

    _handle_content_start = _TagRenderer.div_start(clsnames=('content',))
    _handle_content_end = _TagRenderer.div_end()

    _handle_paragraph_start = _TagRenderer.div_start(clsnames=('paragraph',)), _TagRenderer.p_start()
    _handle_paragraph_end = _TagRenderer.p_end(), _TagRenderer.div_end()

    _handle_image_block_start = _TagRenderer.div_start(clsnames=('imageblock',))
    _handle_image_block_end = _TagRenderer.div_end()

    _handle_preamble_start = _TagRenderer.div_start(id='preamble')
    _handle_preamble_end = _TagRenderer.div_end()

    _handle_top = _TagRenderer.div_start(id='top'), _TagRenderer.div_end()

    def _handle_navlink_start(self, attrs):
        attrs = self.make_attrs(attrs, cls='')
        li = self.make_tag_start(
            'li', self._get_attrs(attrs, 'class', 'id', 'style'))
        a_attrs = self._get_attrs(attrs, 'href', 'target', 'new-tab')
        a = self.make_a_start(a_attrs)
        return li + a

    def _handle_navlink_end(self):
        return self.make_tag_end('a') + self.make_tag_end('li')

    def _handle_nav_start(self, attrs):
        self.tags['nav'].put(attrs)
        if 'sub' in attrs:
            return self.make_tag_start('ul', self.add_class(attrs, 'sub-nav'))
        return self.make_tag_start('nav', attrs)

    def _handle_nav_end(self):
        attrs = self.tags['nav'].get()
        if 'sub' in attrs:
            return self.make_tag_end('ul')
        return self.make_tag_end('nav')

    _handle_a_start = _TagRenderer.a_start()

    def _handle_menu_toggle(self, _):
        li_start = self.make_tag_start(
            'li', {'class': 'toggle-topbar menu-icon'})
        a_start = self.make_tag_start('a', {'href': '#'})
        span_start = self.make_tag_start('span')
        menu = 'Menu'
        span_end = self.make_tag_end('span')
        a_end = self.make_tag_end('a')
        li_end = self.make_tag_end('li')
        return li_start + a_start + span_start + menu + span_end + a_end + li_end

    def _handle_viewport(self, attrs):
        attrs = self.make_attrs(
            attrs, width='device-width', initial_scale='1.0')
        return self.make_tag_startend(
            'meta',
            {
                'name': 'viewport',
                'content': f'width={attrs["width"]}, initial-scale={attrs["initial-scale"]}'
            }
        )

    _handle_description = _meta('description')
    _handle_keywords = _meta('keywords')

    _handle_header = _includer('/includes/header.shtml')
    _handle_footer = _includer('/includes/footer.shtml')

    def _handle_set(self, attrs):
        for k, v in attrs.items():
            self.context[k] = ContextItem(k, self.populate(v))
            # re_compile(f'\\{{\\{{ *{k} *\\}}\\}}'), re_escape(v)

    def _handle_include(self, attrs):
        attrs = self.make_attrs(attrs)
        path = 'templates/' + attrs['src']
        path_parts = (p for p in path.split('/') if p)
        self.__class__(context=self.context,
                       blocks=self.blocks).render(*path_parts)

    def _handle_title(self, _):
        return self.make_tag_start('title') + self.context.get('title', '').raw_v + self.make_tag_end('title')

    def _handle_accordion_start(self, attrs):
        attrs = self.make_attrs(attrs)
        attrs = self.add_class(attrs, 'accordion')
        tag_type = self.get_list_tag(attrs.get('type'))
        del attrs['type']
        self.accordions.append(tag_type)
        return self.make_tag_start(tag_type, attrs)

    @_TagRenderer._make_tag_end
    def _handle_accordion_end(self):
        return self.accordions.pop()

    def _handle_block(self, attrs):
        return self.blocks[attrs['name']].print()

    def _handle_block_start(self, attrs):
        name = attrs['name']
        self.block_names.append(name)
        self.blocks[name] = _RenderStream()
        sys.stdout = self.blocks[name]

    @staticmethod
    def _handle_block_end():
        sys.stdout = sys.__stdout__

    def _handle_extends_start(self, attrs):
        return self.extends.put(attrs)

    def _handle_extends_end(self):
        attrs = self.extends.get()
        base = attrs.get('base', 'base.html')
        return self.include(path=base)

    _handle_code_start = make_codelike_start()
    _handle_code_end = make_codelike_end('code')

    _handle_pre_start = make_codelike_start()
    _handle_pre_end = make_codelike_end('pre')

    _handle_pdf_link_start = _TagRenderer.a_start(clsnames=('pdf',))
    _handle_pdf_link_end = _TagRenderer.a_end()

    _handle_arabic_start = _TagRenderer.div_start(clsnames=('olist', 'arabic',)), _TagRenderer.ol_start()
    _handle_arabic_end = _TagRenderer.ol_end(), _TagRenderer.div_end()

    def _handle_section_start(self, attrs):
        self.tags['section'].put(attrs)
        section_type = attrs.get('type', '')
        if section_type == 'body':
            return _TagRenderer.section_start(clsnames=('sectionbody',))(self, attrs)
        if section_type == '1':
            return _TagRenderer.section_start(clsnames=('sect1',))(self, attrs)
        return _TagRenderer.section_start()(self, attrs)

    def _handle_section_end(self):
        attrs = self.tags['section'].get()
        section_type = attrs.get('type', '')
        if section_type in ('body', '1',):
            return _TagRenderer.section_end()(self)
        _TagRenderer.section_end()(self)



@export
def render(*filename):
    _Renderer().render(*filename)
