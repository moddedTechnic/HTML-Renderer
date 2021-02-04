from html_renderer.selector import selector
from os.path import abspath, dirname, join
from unittest import TestCase, main

# from html_renderer.parser import Parser
from html_renderer.attributes import Class

# from html_renderer.selector import selector

log_file = join(dirname(abspath(__file__)), 'log.txt')

def log(*msg, sep: str = ' ', method = str):
    with open(log_file, 'a') as f:
        f.write(sep.join(method(m) for m in msg) + '\n')


with open(log_file, 'a') as f:
    f.write('\n\n=============== RESTART ===============\n')
    
# p = Parser()
# p.parse('templates', 'includes', 'header.shtml')
# log(p.result)


class TestRenderer(TestCase):
    def test_Class(self):
        log('test_Class')
        c = Class()
        self.assertTrue(isinstance(c.value, set))
        self.assertEqual(len(c), 0)
        c += 'header'
        self.assertEqual(len(c), 1)
        c += Class() + 'banner'
        self.assertEqual(len(c), 2)
        self.assertEqual(c, 'header banner')
        log(c, method=repr)
        log(c)
        log(c, method=selector)

main()
