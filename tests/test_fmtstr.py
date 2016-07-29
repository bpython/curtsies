# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import unittest
from curtsies.formatstring import (FmtStr, fmtstr, Chunk, linesplit,
                                   normalize_slice, width_aware_slice)
from curtsies.fmtfuncs import *
from curtsies.termformatconstants import FG_COLORS
from curtsies.formatstringarray import fsarray, FSArray, FormatStringTest

try:
    from unittest import skip
except ImportError:
    def skip(f):
        return lambda self: None

PY2 = sys.version_info[0] == 2

try:
    unicode = unicode
except:
    unicode = str


def repr_without_leading_u(s):
    assert isinstance(s, type(u''))
    if PY2:
        r = repr(s)
        assert r[0] == 'u'
        return r[1:]
    else:
        return repr(s)


class TestFmtStrInitialization(unittest.TestCase):
    def test_bad(self):
        # Can't specify fg or bg color two ways
        self.assertRaises(ValueError, fmtstr, 'hello', 'blue', {'fg': 30})
        self.assertRaises(ValueError, fmtstr, 'hello', 'on_blue', {'bg': 40})
        # Only specific fg and bg colors are allowed
        self.assertRaises(ValueError, fmtstr, 'hello', {'bg': 30})
        self.assertRaises(ValueError, fmtstr, 'hello', {'fg': 40})
        # Only existing xforms can be used in kwargs
        self.assertRaises(ValueError, fmtstr, 'hello', 'make it big')

    def test_actual_init(self):
        FmtStr()


class TestFmtStrParsing(unittest.TestCase):
    def test_no_escapes(self):
        self.assertEqual(str(fmtstr('abc')), 'abc')

    def test_simple_escapes(self):
        self.assertEqual(str(fmtstr('\x1b[33mhello\x1b[0m')), '\x1b[33mhello\x1b[39m')
        self.assertEqual(str(fmtstr('\x1b[33mhello\x1b[39m')), '\x1b[33mhello\x1b[39m')
        self.assertEqual(str(fmtstr('\x1b[33mhello')), '\x1b[33mhello\x1b[39m')
        self.assertEqual(str(fmtstr('\x1b[43mhello\x1b[49m')), '\x1b[43mhello\x1b[49m')
        self.assertEqual(str(fmtstr('\x1b[43mhello\x1b[0m')), '\x1b[43mhello\x1b[49m')
        self.assertEqual(str(fmtstr('\x1b[43mhello')), '\x1b[43mhello\x1b[49m')
        self.assertEqual(str(fmtstr('\x1b[33m\x1b[43mhello\x1b[0m')),
                         '\x1b[33m\x1b[43mhello\x1b[49m\x1b[39m')

    def test_out_of_order(self):
        self.assertEqual(str(fmtstr('\x1b[33m\x1b[43mhello\x1b[39m\x1b[49m')),
                         '\x1b[33m\x1b[43mhello\x1b[49m\x1b[39m')

    def test_noncurtsies_output(self):
        fmtstr('\x1b[35mx\x1b[m')
        self.assertEqual(fmtstr('\x1b[Ahello'), 'hello')
        self.assertEqual(fmtstr('\x1b[20Ahello'), 'hello')
        self.assertEqual(fmtstr('\x1b[20mhello'), 'hello')


class TestImmutability(unittest.TestCase):

    def test_fmt_strings_remain_unchanged_when_used_to_construct_other_ones(self):
        a = fmtstr('hi', 'blue')
        b = fmtstr('there', 'red')
        c = a + b
        green(c)
        self.assertEqual(a.shared_atts['fg'], FG_COLORS['blue'])
        self.assertEqual(b.shared_atts['fg'], FG_COLORS['red'])

    def test_immutibility_of_FmtStr(self):
        a = fmtstr('hi', 'blue')
        b = green(a)
        self.assertEqual(a.shared_atts['fg'], FG_COLORS['blue'])
        self.assertEqual(b.shared_atts['fg'], FG_COLORS['green'])


class TestFmtStrSplice(unittest.TestCase):

    def test_simple_beginning_splice(self):
        self.assertEqual(fmtstr('abc').splice('d', 0), fmtstr('dabc'))
        self.assertEqual(fmtstr('abc').splice('d', 0), 'd'+fmtstr('abc'))

    def test_various_splices(self):
        a = blue('hi')
        b = a + green('bye')
        c = b + red('!')
        self.assertEqual(c.splice('asdfg', 1),
                         blue('h')+'asdfg'+blue('i')+green('bye')+red('!'))
        self.assertEqual(c.splice('asdfg', 1, 4),
                         blue('h')+'asdfg'+green('e')+red('!'))
        self.assertEqual(c.splice('asdfg', 1, 5),
                         blue('h')+'asdfg'+red('!'))

    def test_splice_of_empty_fmtstr(self):
        self.assertEqual(fmtstr('ab').splice('', 1), fmtstr('ab'))

    def test_splice_with_multiple_basefmtstrs(self):
        a = fmtstr('notion')
        b = a.splice('te', 2, 6)
        c = b.splice('de', 0)

        self.assertEqual(a.s, "notion")
        self.assertEqual(b.s, "note")
        self.assertEqual(c.s, "denote")
        self.assertEqual(len(c.basefmtstrs), 3)

    def test_splice_fmtstr_with_end_without_atts(self):
        a = fmtstr('notion')
        b = a.splice('te', 2, 6)

        self.assertEqual(a.s, "notion")
        self.assertEqual(b.s, "note")
        self.assertEqual(len(b.basefmtstrs), 2)

    def test_splice_fmtstr_with_end_with_atts(self):
        # Need to test with fmtstr consisting of multiple basefmtstrs
        # and with attributes
        a = fmtstr('notion', 'blue')
        b = a.splice('te', 2, 6)

        self.assertEqual(a.s, "notion")
        self.assertEqual(a.basefmtstrs[0].atts, {'fg': 34})
        self.assertEqual(len(a.basefmtstrs), 1)

        self.assertEqual(b.s, 'note')
        self.assertEqual(b.basefmtstrs[0].atts, {'fg': 34})
        self.assertEqual(b.basefmtstrs[1].atts, {})
        self.assertEqual(len(b.basefmtstrs), 2)

    def test_splice_fmtstr_without_end(self):
        a = fmtstr('notion')
        b = a.splice(fmtstr('ta'), 2)
        self.assertEqual(a.s, 'notion')
        self.assertEqual(b.s, 'notation')
        self.assertEqual(len(b.basefmtstrs), 3)

    def test_splice_string_without_end(self):
        a = fmtstr('notion')
        b = a.splice('ta', 2)
        self.assertEqual(a.s, 'notion')
        self.assertEqual(b.s, 'notation')
        self.assertEqual(len(b.basefmtstrs), 3)

    def test_multiple_bfs_splice(self):
        self.assertEqual(fmtstr('a') + blue('b'),
                         on_blue(' '*2).splice(fmtstr('a')+blue('b'), 0, 2))
        self.assertEqual(on_red('yo') + on_blue('   '),
                         on_blue(' '*5).splice(on_red('yo'), 0, 2))
        self.assertEqual(' ' + on_red('yo') + on_blue('   '),
                         on_blue(' '*6).splice(' ' + on_red('yo'), 0, 3))
        self.assertEqual(on_blue("hey") + ' ' + on_red('yo') + on_blue('   '),
                         on_blue(' '*9).splice(on_blue("hey") + ' ' + on_red('yo'), 0, 6))
        self.assertEqual(on_blue(' '*5) + on_blue("hey") + ' ' + on_red('yo') + on_blue('   '),
                         on_blue(' '*14).splice(on_blue("hey") + ' ' + on_red('yo'), 5, 11))

class TestFmtStr(unittest.TestCase):

    def test_copy_with_new_atts(self):
        a = fmtstr('hello')
        b = a.copy_with_new_atts(bold=True)
        self.assertEqual(a.shared_atts, {})
        self.assertEqual(b.shared_atts, {'bold': True})

    def test_copy_with_new_str(self):
        # Change string but not attributes
        a = fmtstr('hello', 'blue')
        b = a.copy_with_new_str('bye')
        self.assertEqual(a.s, 'hello')
        self.assertEqual(b.s, 'bye')
        self.assertEqual(a.basefmtstrs[0].atts, b.basefmtstrs[0].atts)

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

    def test_new_with_atts_removed(self):
        a = fmtstr('hi', 'blue', 'on_green')
        b = fmtstr('there', 'blue', 'on_red')
        c = a + b
        self.assertEqual(c.new_with_atts_removed('fg'), on_green('hi')+on_red('there'))

    def setUp(self):
        self.s = fmtstr('hello!', 'on_blue', fg='red')

    def test_length(self):
        self.assertEqual(len(self.s), len(self.s.s))

    def test_split(self):
        self.assertEqual(blue('hello there').split(' '), [blue('hello'), blue('there')])
        s = blue('hello there')
        self.assertEqual(s.split(' '), [s[:5], s[6:]])

        # split shouldn't create fmtstrs without basefmtstrs
        self.assertEqual(fmtstr('a').split('a')[0].basefmtstrs, fmtstr('').basefmtstrs)
        self.assertEqual(fmtstr('a').split('a')[1].basefmtstrs, fmtstr('').basefmtstrs)

        self.assertEqual((fmtstr('imp') + ' ').split('i'), [fmtstr(''), fmtstr('mp') + ' '])
        self.assertEqual(blue('abcbd').split('b'), [blue('a'), blue('c'), blue('d')])

    def test_split_with_spaces(self):
        self.assertEqual(blue('a\nb').split(), [blue('a'), blue('b')])
        self.assertEqual(blue('a   \t\n\nb').split(), [blue('a'), blue('b')])
        self.assertEqual(blue('hello   \t\n\nthere').split(), [blue('hello'), blue('there')])

    def test_ljust_rjust(self):
        """"""
        b = fmtstr(u'ab', 'blue', 'on_red', 'bold')
        g = fmtstr(u'cd', 'green', 'on_red', 'bold')
        s = b + g
        self.assertEqual(s.ljust(6), b + g + on_red('  '))
        self.assertEqual(s.rjust(6), on_red('  ') + b + g)

        # doesn't add empties to end
        self.assertEqual(s.ljust(4), b + g)
        self.assertEqual(s.rjust(4), b + g)

        # behavior if background different
        s = on_blue('a') + on_green('b')
        self.assertEqual(s.ljust(3), fmtstr('ab '))
        self.assertEqual(s.rjust(3), fmtstr(' ab'))
        s = blue(on_blue('a')) + green(on_green('b'))
        self.assertEqual(s.ljust(3), blue('a') + green('b') + fmtstr(' '))
        self.assertEqual(s.rjust(3), fmtstr(' ') + blue('a') + green('b'))

        #using fillchar
        self.assertEqual(s.ljust(3, '*'), fmtstr('ab*'))
        self.assertEqual(s.rjust(3, '*'), fmtstr('*ab'))

        #TODO:  (not tested or implemented)
        # formatted string passed in
        # preserve some non-uniform styles (bold, dark, blink) but not others (underline, invert)

    def test_linessplit(self):
        text = blue('the sum of the squares of the sideways')
        result = [blue('the')+blue(' ')+blue('sum'),
                  blue('of')+blue(' ')+blue('the'),
                  blue('squares'),
                  blue('of')+blue(' ')+blue('the'),
                  blue('sideway'),
                  blue('s')
                  ]
        self.assertEqual(linesplit(text, 7), result)

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

    def test_repr(self):
        self.assertEqual(fmtstr('hello', 'red', bold=False), red('hello'))
        self.assertEqual(fmtstr('hello', 'red', bold=True), bold(red('hello')))


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
        s = fmtstr('imp') + ' '
        self.assertEqual(s[1:], fmtstr('mp')+' ')
        self.assertEqual(blue('a\nb')[0:1], blue('a'))

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

    def test_normal_chars(self):
        fmtstr('a', 'blue')
        str(fmtstr('a', 'blue'))
        unicode(fmtstr('a', 'blue'))
        self.assertTrue(True)

    def test_funny_chars(self):
        fmtstr('⁇', 'blue')
        str(Chunk('⁇', {'fg': 'blue'}))
        str(fmtstr('⁇', 'blue'))
        unicode(fmtstr('⁇', 'blue'))
        self.assertTrue(True)

    def test_right_sequence_in_py3(self):
        red_on_blue = fmtstr('hello', 'red', 'on_blue')
        blue_on_red = fmtstr('there', fg='blue', bg='red')
        green_s = fmtstr('!', 'green')
        full = red_on_blue + ' ' + blue_on_red + green_s
        self.assertEqual(full, on_blue(red("hello"))+" "+on_red(blue("there"))+green("!"))
        self.assertEqual(str(full), '\x1b[31m\x1b[44mhello\x1b[49m\x1b[39m \x1b[34m\x1b[41mthere\x1b[49m\x1b[39m\x1b[32m!\x1b[39m')

    def test_len_of_unicode(self):
        self.assertEqual(len(fmtstr('┌─')), 2)
        lines = ['┌─', 'an', '┌─']
        r = fsarray(lines)
        self.assertEqual(r.shape, (3, 2))
        self.assertEqual(len(fmtstr(fmtstr('┌─'))), len(fmtstr('┌─')))
        self.assertEqual(fmtstr(fmtstr('┌─')), fmtstr('┌─'))
        #TODO should we make this one work?
        # always coerce everything to unicode?
        #self.assertEqual(len(fmtstr('┌─')), 2)

    def test_len_of_unicode_in_fsarray(self):

        fsa = FSArray(3, 2)
        fsa.rows[0] = fsa.rows[0].setslice_with_length(0, 2, '┌─', 2)
        self.assertEqual(fsa.shape, (3, 2))
        fsa.rows[0] = fsa.rows[0].setslice_with_length(0, 2, fmtstr('┌─', 'blue'), 2)
        self.assertEqual(fsa.shape, (3, 2))

    def test_add_unicode_to_byte(self):
        fmtstr('┌') + fmtstr('a')
        fmtstr('a') + fmtstr('┌')
        '┌' + fmtstr('┌')
        '┌' + fmtstr('a')
        fmtstr('┌') + '┌'
        fmtstr('a') + '┌'

    def test_unicode_slicing(self):
        self.assertEqual(fmtstr('┌adfs', 'blue')[:2], fmtstr('┌a', 'blue'))
        self.assertEqual(type(fmtstr('┌adfs', 'blue')[:2].s), type(fmtstr('┌a', 'blue').s))
        self.assertEqual(len(fmtstr('┌adfs', 'blue')[:2]), 2)

    def test_unicode_repr(self):
        repr(Chunk('–'))
        self.assertEqual(repr(fmtstr('–')), repr_without_leading_u('–'))


class TestCharacterWidth(unittest.TestCase):

    def test_doublewide_width(self):
        self.assertEqual(len(fmtstr('Ｅ', 'blue')), 1)
        self.assertEqual(fmtstr('Ｅ', 'blue').width, 2)
        self.assertEqual(len(fmtstr('ｈｉ')), 2)
        self.assertEqual(fmtstr('ｈｉ').width, 4)

    def test_multi_width(self):
        self.assertEqual(len(fmtstr('a\u0300')), 2)
        self.assertEqual(fmtstr('a\u0300').width, 1)

    def test_width_aware_slice(self):
        self.assertEqual(fmtstr('Ｅ').width_aware_slice(slice(None, 1, None)).s, ' ')
        self.assertEqual(fmtstr('Ｅ').width_aware_slice(slice(None, 2, None)).s, 'Ｅ')
        self.assertEqual(fmtstr('HＥ!', 'blue').width_aware_slice(slice(1, 2, None)), fmtstr(' ', 'blue'))
        self.assertEqual(fmtstr('HＥ!', 'blue').width_aware_slice(slice(1, 3, None)), fmtstr('Ｅ', 'blue'))

    def test_width_at_offset(self):
        self.assertEqual(fmtstr('abＥcdef').width_at_offset(0), 0)
        self.assertEqual(fmtstr('abＥcdef').width_at_offset(2), 2)
        self.assertEqual(fmtstr('abＥcdef').width_at_offset(3), 4)
        self.assertEqual(fmtstr('a\u0300b\u3000c').width_at_offset(0), 0)
        self.assertEqual(fmtstr('a\u0300b\u3000c').width_at_offset(1), 1)
        self.assertEqual(fmtstr('a\u0300b\u3000c').width_at_offset(2), 1)
        self.assertEqual(fmtstr('a\u0300b\u3000c').width_at_offset(3), 2)
        self.assertEqual(len(fmtstr('a\u0300')), 2)
        self.assertEqual(fmtstr('a\u0300').width, 1)

class TestWidthHelpers(unittest.TestCase):

    def test_combining_char_aware_slice(self):
        self.assertEqual(width_aware_slice('abc', 0, 2), 'ab')
        self.assertEqual(width_aware_slice('abc', 1, 3), 'bc')
        self.assertEqual(width_aware_slice('abc', 0, 3), 'abc')
        self.assertEqual(width_aware_slice('ab\u0300c', 0, 3), 'ab\u0300c')
        self.assertEqual(width_aware_slice('ab\u0300c', 0, 2), 'ab\u0300')
        self.assertEqual(width_aware_slice('ab\u0300c', 1, 3), 'b\u0300c')
        self.assertEqual(width_aware_slice('ab\u0300\u0300c', 1, 3), 'b\u0300\u0300c')

    def test_char_width_aware_slice(self):
        self.assertEqual(width_aware_slice('abc', 1, 2), 'b')
        self.assertEqual(width_aware_slice('aＥbc', 0, 4), 'aＥb')
        self.assertEqual(width_aware_slice('aＥbc', 1, 4), 'Ｅb')
        self.assertEqual(width_aware_slice('aＥbc', 2, 4), ' b')
        self.assertEqual(width_aware_slice('aＥbc', 0, 2), 'a ')


class TestFSArray(unittest.TestCase):
    def test_no_hanging_space(self):
        a = FSArray(4, 2)
        self.assertEqual(len(a.rows[0]), 0)

    def test_assignment_working(self):
        t = FSArray(10, 10)
        t[2, 2] = 'a'
        t[2, 2] == 'a'

    def test_normalize_slice(self):
        class SliceBuilder(object):
            def __getitem__(self, slice):
                return slice
        Slice = SliceBuilder()

        self.assertEqual(normalize_slice(10, Slice[:3]), slice(0, 3, None))
        self.assertEqual(normalize_slice(11, Slice[3:]), slice(3, 11, None))

    @skip('TODO')
    def test_oomerror(self):
        a = FSArray(10, 40)
        a[2:-2, 2:-2] = fsarray(['asdf', 'zxcv'])


class TestFSArrayWithDiff(FormatStringTest):

    def test_diff_testing(self):
        a = fsarray(['abc', 'def'])
        b = fsarray(['abc', 'dqf'])
        self.assertRaises(AssertionError, self.assertFSArraysEqual, a, b)
        a = fsarray([blue('abc'), red('def')])
        b = fsarray([blue('abc'), red('dqf')])
        self.assertRaises(AssertionError, self.assertFSArraysEqual, a, b)
        a = fsarray([blue('abc'), red('def')])
        b = fsarray([blue('abc'), red('d')+blue('e')+red('f')])
        self.assertRaises(AssertionError, self.assertFSArraysEqual, a, b)
        a = fsarray(['abc', 'def'])
        b = fsarray(['abc', 'def'])
        self.assertFSArraysEqual(a, b)
        a = fsarray([blue('abc'), red('def')])
        b = fsarray([blue('abc'), red('def')])
        self.assertFSArraysEqual(a, b)

if __name__ == '__main__':
    import fmtstr.fmtstr
    unittest.main()
