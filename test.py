# -*- coding: utf-8 -*-
import unittest
from fmtstr.fmtstr import FmtStr
from fmtstr.fmtfuncs import *
from fmtstr.escseqparse import parse

try:
    unicode = unicode
except:
    unicode = str

class TestFmtStrInitialization(unittest.TestCase):
    def test_bad(self):
        # Can't specify fg or bg color two ways
        self.assertRaises(ValueError, fmtstr, 'hello', 'blue', {'fg':30})
        self.assertRaises(ValueError, fmtstr, 'hello', 'on_blue', {'bg':40})
        # Only specific fg and bg colors are allowed
        self.assertRaises(ValueError, fmtstr, 'hello', {'bg':30})
        self.assertRaises(ValueError, fmtstr, 'hello', {'fg':40})
        # Only existing xforms can be used in kwargs
        self.assertRaises(ValueError, fmtstr, 'hello', 'make it big')

    def test_actual_init(self):
        FmtStr()

class TestFmtStr(unittest.TestCase):

    def setUp(self):
        self.s = fmtstr('hello!', 'on_blue', fg='red')

    def test_length(self):
        self.assertEqual(len(self.s), len(self.s.s))

    #def test_sample(self):
        #with self.assertRaises(ValueError):
            #random.sample(self.seq, 20)
        #for element in random.sample(self.seq, 5):
            #self.assertTrue(element in self.seq)

class TestDoubleUnders(unittest.TestCase):
    def test_equality(self):
        x = fmtstr("adfs")
        self.assertEqual(x, x)
        self.assertTrue(fmtstr("adfs"), fmtstr("adfs"))
        self.assertTrue(fmtstr("adfs", 'blue'), fmtstr("adfs", fg='blue'))

class TestConvenience(unittest.TestCase):
    def test_fg(self):
        red('asdf')
        blue('asdf')
        self.assertTrue(True)

    def test_bg(self):
        on_red('asdf')
        on_blue('asdf')
        self.assertTrue(True)

    def test_styles(self):
        underline('asdf')
        blink('asdf')
        self.assertTrue(True)

class TestSlicing(unittest.TestCase):
    def test_index(self):
        self.assertEqual(fmtstr('Hi!', 'blue')[0], fmtstr('H', 'blue'))
        self.assertRaises(IndexError, fmtstr('Hi!', 'blue').__getitem__, 5)
    def test_slice(self):
        self.assertEqual(fmtstr('Hi!', 'blue')[1:2], fmtstr('i', 'blue'))
        self.assertEqual(fmtstr('Hi!', 'blue')[1:], fmtstr('i!', 'blue'))
        self.assertEqual(fmtstr('Hi!', 'blue')[15:18], fmtstr('', 'blue'))

    def AWLKJAS_set_index(self):
        f = fmtstr('Hi!', 'blue')
        self.assertRaises(IndexError, f.__setitem__, 12, 'a')
        f = fmtstr('Hi!', 'blue')
        f[1] = fmtstr('o')
        changed = blue('H') + plain('o') + blue('!')
        self.assertEqual(str(f), str(changed))
        self.assertEqual(f, changed)


class TestComposition(unittest.TestCase):

    def test_simple_composition(self):
        a = fmtstr('hello ', 'underline', 'on_blue')
        b = fmtstr('there', 'red', 'on_blue')
        c = a + b
        fmtstr(c, bg='red')
        self.assertTrue(True)


class TestUnicode(unittest.TestCase):

    def test_output_type(self):
        self.assertEqual(type(str(fmtstr('hello', 'blue'))), str)
        self.assertEqual(type(unicode(fmtstr('hello', 'blue'))), unicode)
        self.assertEqual(type(str(fmtstr(u'hello', 'blue'))), str)
        self.assertEqual(type(unicode(fmtstr(u'hello', 'blue'))), unicode)

    def test_normal_chars(self):
        fmtstr('a', 'blue')
        fmtstr(u'a', 'blue')
        str(fmtstr('a', 'blue'))
        str(fmtstr(u'a', 'blue'))
        unicode(fmtstr('a', 'blue'))
        unicode(fmtstr(u'a', 'blue'))
        self.assertTrue(True)

    def test_funny_chars(self):
        fmtstr('⁇', 'blue')
        fmtstr(u'⁇', 'blue')
        fmtstr(u'⁇', 'blue')
        str(fmtstr('⁇', 'blue'))
        str(fmtstr(u'⁇', 'blue'))
        unicode(fmtstr('⁇', 'blue'))
        unicode(fmtstr(u'⁇', 'blue'))
        self.assertTrue(True)

    def right_sequence_in_py3(self):
        red_on_blue = fmtstr('hello', 'red', 'on_blue')
        blue_on_red = fmtstr('there', fg='blue', bg='red')
        green = fmtstr('!', 'green')
        full = red_on_blue + ' ' + blue_on_red + green
        self.assertEqual(full, on_blue(red("hello"))+" "+on_red(blue("there"))+green("!"))
        self.assertEqual(str(full), '\x1b[31m\x1b[44mhello\x1b[49m\x1b[39m \x1b[34m\x1b[41mthere\x1b[49m\x1b[39m\x1b[32m!\x1b[39m')

class TestRemovalOfBlanks(unittest.TestCase):
    def test_parse_empties(self):
        pass

if __name__ == '__main__':
    import fmtstr.fmtstr
    unittest.main()
