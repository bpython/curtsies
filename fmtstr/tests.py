import unittest
from .fmtstr import *

class TestFmtStrInitialization(unittest.TestCase):
    def test_bad(self):
        # Can't specify fg or bg color two ways
        self.assertRaises(ValueError, FmtStr, 'hello', 'blue', {'fg':30})
        self.assertRaises(ValueError, FmtStr, 'hello', 'on_blue', {'bg':40})
        # Only specific fg and bg colors are allowed
        self.assertRaises(ValueError, FmtStr, 'hello', {'bg':30})
        self.assertRaises(ValueError, FmtStr, 'hello', {'fg':40})
        # Only existing xforms can be used in kwargs
        self.assertRaises(ValueError, FmtStr, 'hello', 'make it big')

class TestFmtStr(unittest.TestCase):

    def setUp(self):
        self.s = FmtStr('hello!', 'on_blue', fg='red')

    def test_length(self):
        self.assertEqual(len(self.s), len(self.s.string))

    #def test_sample(self):
        #with self.assertRaises(ValueError):
            #random.sample(self.seq, 20)
        #for element in random.sample(self.seq, 5):
            #self.assertTrue(element in self.seq)

class TestDoubleUnders(unittest.TestCase):
    def test_equality(self):
        x = FmtStr("adfs")
        self.assertEqual(x, x)
        self.assertTrue(FmtStr("adfs"), FmtStr("adfs"))
        self.assertTrue(FmtStr("adfs", 'blue'), FmtStr("adfs", fg='blue'))

class TestConvenience(unittest.TestCase):
    def test_fg(self):
        red('asdf')
        blue('asdf')
        self.assertTrue(True)

    def test_bg(self):
        on_red('asdf')
        on_blue('asdf')
        self.assertTrue(True)

    def test_text_xforms(self):
        upper('asdf')
        title('asdf')
        self.assertTrue(True)

    def test_styles(self):
        underline('asdf')
        blink('asdf')
        self.assertTrue(True)

class TestSlicing(unittest.TestCase):
    def test_index(self):
        self.assertEqual(FmtStr('Hi!', 'blue')[0], FmtStr('H', 'blue'))
        self.assertRaises(IndexError, FmtStr('Hi!', 'blue').__getitem__, 5)
    def test_slice(self):
        self.assertEqual(FmtStr('Hi!', 'blue')[1:2], FmtStr('i', 'blue'))
        self.assertEqual(FmtStr('Hi!', 'blue')[1:], FmtStr('i!', 'blue'))
        self.assertEqual(FmtStr('Hi!', 'blue')[15:18], FmtStr('', 'blue'))

    def AWLKJAS_set_index(self):
        f = FmtStr('Hi!', 'blue')
        self.assertRaises(IndexError, f.__setitem__, 12, 'a')
        f = FmtStr('Hi!', 'blue')
        f[1] = FmtStr('o')
        changed = blue('H') + plain('o') + blue('!')
        self.assertEqual(str(f), str(changed))
        self.assertEqual(f, changed)


class TestComposition(unittest.TestCase):

    def test_simple_composition(self):
        a = FmtStr('hello ', 'underline', 'on_blue')
        b = FmtStr('there', 'red', 'on_blue')
        c = a + b
        fmtstr(c, bg='red')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
