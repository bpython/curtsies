import unittest
from .fmtstr import *
from .bpythonparse import string_to_fmtstr
from .escseqparse import parse

class TestManyBrackets(unittest.TestCase):
    def test_three_brackets(self):
        fs = string_to_fmtstr('[][][]')
        fs2 = parse(str(fs))
        self.assertEqual(fs, fs2)
    def test_four_brackets(self):
        fs = string_to_fmtstr('[][][][]')
        fs2 = parse(str(fs))
        self.assertEqual(fs, fs2)

if __name__ == '__main__':
    unittest.main()
    #print string_to_fmtstr('[][][][]')
    #print parse(str(string_to_fmtstr('[][][][]')))
