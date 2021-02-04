from html_renderer.parser import Parser
from html_renderer.attributes import Class
from html_renderer.selector import selector

# p = Parser()
# p.parse('templates', 'includes', 'header.shtml')
# log(p.result)

def log(*msg, sep: str = ' ', method = str):
    with open('out.txt', 'a') as f:
        f.write(sep.join(method(m) for m in msg) + '\n')


if __name__ == '__main':
    with open('out.txt', 'w') as f:
        f.write('')
    
    c = Class()
    c += 'header'
    c += Class() + 'banner'

    log(c, method=repr)
    log(c)
    log(selector(c))
