# -*- coding: utf-8 -*-
import unittest
from fmtstr.fmtstr import FmtStr, fmtstr, BaseFmtStr
from fmtstr.fmtfuncs import *
from fmtstr.termformatconstants import FG_COLORS
from fmtstr.escseqparse import parse
from fmtstr.fsarray import fsarray, FSArray

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

class TestImmutability(unittest.TestCase):

    def test_fmt_strings_remain_unchanged_when_used_to_construct_other_ones(self):
        a = fmtstr('hi', 'blue')
        b = fmtstr('there', 'red')
        c = a + b
        d = green(c)
        self.assertEqual(a.shared_atts['fg'], FG_COLORS['blue'])
        self.assertEqual(b.shared_atts['fg'], FG_COLORS['red'])
        
    def test_immutibility_of_FmtStr(self):
        a = fmtstr('hi', 'blue')
        b = green(a)
        self.assertEqual(a.shared_atts['fg'], FG_COLORS['blue'])
        self.assertEqual(b.shared_atts['fg'], FG_COLORS['green'])

class TestFmtStr(unittest.TestCase):

    def test_copy_with_new_atts(self):
        a = fmtstr('hello')
        b = a.copy_with_new_atts(bold = True)
        self.assertEqual(a.shared_atts, {})
        self.assertEqual(b.shared_atts, {'bold': True})

    def test_copy_with_new_str(self):
        # Change string but not attributes
        a = fmtstr('hello', 'blue')
        b = a.copy_with_new_str('bye')
        self.assertEqual(a.s, 'hello')
        self.assertEqual(b.s, 'bye')
        self.assertEqual(a.basefmtstrs[0].atts, b.basefmtstrs[0].atts)

    def test_insert_with_multiple_basefmtstrs(self):
        a = fmtstr('notion')
        b = a.insert('te', 2, 6)
        c = b.insert('de', 0)

        self.assertEqual(a.s, "notion")
        self.assertEqual(b.s, "note")
        self.assertEqual(c.s, "denote")
        self.assertEqual(len(c.basefmtstrs), 3)

    def test_insert_fmtstr_with_end_without_atts(self):
        a = fmtstr('notion')
        b = a.insert('te', 2, 6)

        self.assertEqual(a.s, "notion")
        self.assertEqual(b.s, "note")
        self.assertEqual(len(b.basefmtstrs), 2)

    def test_insert_fmtstr_with_end_with_atts(self):
        # Need to test with fmtstr consisting of multiple basefmtstrs
        # and with attributes
        a = fmtstr('notion', 'blue')
        b = a.insert('te', 2, 6)

        self.assertEqual(a.s, "notion")
        self.assertEqual(a.basefmtstrs[0].atts, {'fg': 34})
        self.assertEqual(len(a.basefmtstrs), 1)
        
        self.assertEqual(b.s, 'note')
        self.assertEqual(b.basefmtstrs[0].atts, {'fg': 34})
        self.assertEqual(b.basefmtstrs[1].atts, {})
        self.assertEqual(len(b.basefmtstrs), 2)

    def test_insert_fmtstr_without_end(self):
        a = fmtstr('notion')
        b = a.insert(fmtstr('ta'), 2)
        self.assertEqual(a.s, 'notion')
        self.assertEqual(b.s, 'notation')
        self.assertEqual(len(b.basefmtstrs), 3)

    def test_insert_string_without_end(self):
        a = fmtstr('notion')
        b = a.insert('ta', 2)        
        self.assertEqual(a.s, 'notion')
        self.assertEqual(b.s, 'notation')
        self.assertEqual(len(b.basefmtstrs), 3)

    def test_append_without_atts(self):
        a = fmtstr('no')
        b = a.append('te')
        self.assertEqual(a.s, 'no')
        self.assertEqual(b.s, 'note')
        self.assertEqual(len(b.basefmtstrs), 2)

    def test_shared_atts(self):
        a = fmtstr('hi', 'blue')
        b = fmtstr('there', 'blue')
        c = a + b
        self.assertTrue('fg' in a.shared_atts)
        self.assertTrue('fg' in c.shared_atts)

    def setUp(self):
        self.s = fmtstr('hello!', 'on_blue', fg='red')

    def test_length(self):
        self.assertEqual(len(self.s), len(self.s.s))

    def test_split(self):
        self.assertEqual(blue('hello there').split(' '), [blue('hello'), blue('there')])
        s = blue('hello there')
        self.assertEqual(s.split(' '), [s[:5], s[6:]])

    def test_mul(self):
        self.assertEqual(fmtstr('heyhey'), fmtstr('hey')*2)
        pass
        #TODO raise common attributes when doing equality or when
        # doing multiplication, addition etc. to make these pass
        #self.assertEqual(blue('hellohellohello'), blue('hello')*3)
        #self.assertEqual(
        #        bold(blue('hey')+green('there')+blue('hey')+green('there')),
        #        bold(blue('hey')+green('there'))*2)

    def test_change_color(self):
        a = blue(red('hello'))
        self.assertEqual(a, blue('hello'))

class TestBaseFmtStr(unittest.TestCase):
    def test_getitem(self):
        self.assertEqual(BaseFmtStr('hi', {'fg':37})[5], 'h')

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
        # considering changing behavior so that this doens't work
        # self.assertEqual(fmtstr('Hi!', 'blue')[15:18], fmtstr('', 'blue'))

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

    def test_right_sequence_in_py3(self):
        red_on_blue = fmtstr('hello', 'red', 'on_blue')
        blue_on_red = fmtstr('there', fg='blue', bg='red')
        green_s = fmtstr('!', 'green')
        full = red_on_blue + ' ' + blue_on_red + green_s
        self.assertEqual(full, on_blue(red("hello"))+" "+on_red(blue("there"))+green("!"))
        self.assertEqual(str(full), '\x1b[31m\x1b[44mhello\x1b[49m\x1b[39m \x1b[34m\x1b[41mthere\x1b[49m\x1b[39m\x1b[32m!\x1b[39m')

    def test_len_of_unicode(self):
        self.assertEqual(len(fmtstr(u'┌─')), 2)
        lines = [u'┌─', 'an', u'┌─']
        r = fsarray(lines)
        self.assertEqual(r.shape, (3, 2))
        self.assertEqual(len(fmtstr(fmtstr(u'┌─'))), len(fmtstr(u'┌─')))
        self.assertEqual(fmtstr(fmtstr(u'┌─')), fmtstr(u'┌─'))
        #TODO should we make this one work?
        # always coerce everything to unicode?
        #self.assertEqual(len(fmtstr('┌─')), 2)

    def test_len_of_unicode_in_fsarray(self):

        fsa = FSArray(3, 2)
        fsa.rows[0][0:2] = u'┌─'
        self.assertEqual(fsa.shape, (3, 2))
        fsa.rows[0][0:2] = fmtstr(u'┌─', 'blue')
        self.assertEqual(fsa.shape, (3, 2))



        #lines = [u'┌─', 'an', u'┌─']
        #r = fsarray(lines[:3])
        #self.assertEqual(r.shape, (3, 2))
        #self.assertEqual(fsarray(r).shape, (3, 2))
        #self.assertEqual(fsarray(r[:]).shape, (3, 2))
        #self.assertEqual(fsarray(r[:, :]).shape, (3, 2))

    def test_add_unicode_to_byte(self):
        fmtstr(u'┌') + fmtstr('a')
        fmtstr('a') + fmtstr(u'┌')
        u'┌' + fmtstr(u'┌')
        u'┌' + fmtstr('a')
        fmtstr(u'┌') + u'┌'
        fmtstr('a') + u'┌'

    def test_unicode_slicing(self):
        self.assertEqual(fmtstr(u'┌adfs', 'blue')[:2], fmtstr(u'┌a', 'blue'))
        self.assertEqual(type(fmtstr(u'┌adfs', 'blue')[:2].s), type(fmtstr(u'┌a', 'blue').s))
        self.assertEqual(len(fmtstr(u'┌adfs', 'blue')[:2]), 2)

    def test_unicode_repr(self):
        repr(BaseFmtStr(u'–'))
        self.assertEqual(repr(fmtstr(u'–')), repr(u'–'))

class TestRemovalOfBlanks(unittest.TestCase):
    def test_parse_empties(self):
        pass

if __name__ == '__main__':
    import fmtstr.fmtstr
    unittest.main()
