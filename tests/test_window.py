# -*- coding: utf-8 -*-
import unittest
import sys

from curtsies.window import BaseWindow, FullscreenWindow, CursorAwareWindow, Resizer
from curtsies.formatstringarray import FSArray, fsarray, FormatStringTest

if sys.version_info[0] == 3:
    from io import StringIO
else:
    from cStringIO import StringIO
class TestBaseWindow(unittest.TestCase):
    """Pretty pathetic tests for window"""
    def test_window(self):
        fakestdout = StringIO()
        window = BaseWindow(fakestdout)
        window.write('hi')
        fakestdout.seek(0)
        self.assertEqual(fakestdout.read(), 'hi')

    def test_array_from_text(self):
        window = BaseWindow()
        a = window.array_from_text('.\n.\n.')
        self.assertEqual(a.height, 3)
        self.assertEqual(a[0], '.')
        self.assertEqual(a[1], '.')

    def test_array_from_text_rc(self):
        a = BaseWindow.array_from_text_rc('asdfe\nzx\n\n123', 3, 4)
        self.assertEqual(a.height, 3)
        self.assertEqual(a.width, 4)
        self.assertEqual(a[0], 'asdf')
        self.assertEqual(a[1], 'e')
        self.assertEqual(a[2], 'zx')

    def test_fullscreen_window(self):
        fakestdout = StringIO()
        window = FullscreenWindow(fakestdout)
        window.write('hi')
        fakestdout.seek(0)
        self.assertEqual(fakestdout.read(), 'hi')

class TestResizer(FormatStringTest):
    """Tests for predicting how resizing of terminals acts"""
    def assertArraysEqual(self, a, b):
        if isinstance(a, FSArray) and isinstance(b, FSArray):
            self.assertFSArraysEqual(self, a, b)
            return
        self.assertEqual(len(a), len(b), '\n%s\n---\n%s' % ('\n'.join(a), '\n'.join(b)))
        for i, (a_row, b_row) in enumerate(zip(a, b)):
            self.assertEqual(a_row, b_row, 'row %d differs' % (i,))

    def test_validation(self):
        last_rendered_array = ['hello', 'there', 'this is a longer line']
        self.assertRaises(ValueError, Resizer, last_rendered_array, 5, 5, 0) # too narrow
        self.assertRaises(ValueError, Resizer, last_rendered_array, 0, 22, 0) # bad height
        self.assertRaises(ValueError, Resizer, last_rendered_array, 5, 22, -1) # bad top line
        self.assertRaises(ValueError, Resizer, last_rendered_array, 5, 22, 22) # bad top line

    def test_nop(self):
        last_rendered_array = ['hello', 'there', 'this is a longer line']
        r = Resizer(last_rendered_array, 5, 22, 0)
        r.set_new(5, 22)
        self.assertArraysEqual(r.resized_array(), ['hello', 'there', 'this is a longer line'])
        self.assertEqual(r.top_usable_row(), 0)

    def test_drag_down(self):
        last_rendered_array = ['hello', 'there', 'this is a longer line']
        r = Resizer(last_rendered_array, 5, 22, 0)
        r.set_new(6, 22)
        self.assertArraysEqual(r.resized_array(), ['hello', 'there', 'this is a longer line'])
        self.assertEqual(r.top_usable_row(), 1)

    def test_drag_up(self):
        last_rendered_array = ['hello', 'there', 'this is a longer line']
        r = Resizer(last_rendered_array, 5, 22, 2)
        r.set_new(4, 22)
        self.assertArraysEqual(r.resized_array(), ['hello', 'there', 'this is a longer line'])
        self.assertEqual(r.top_usable_row(), 1)

    def test_narrow(self):
        last_rendered_array = ['hello', 'there', 'this is a longer line']
        r = Resizer(last_rendered_array, 5, 22, 1)
        r.set_new(5, 20)
        self.assertArraysEqual(r.resized_array(), ['hello', 'there', 'this is a longer lin', 'e'])
        self.assertEqual(r.top_usable_row(), 0)

    def test_too_big(self):
        last_rendered_array = ['hello', 'there', 'this is a longer line']
        r = Resizer(last_rendered_array, 2, 22, 0)
        r.set_new(5, 22)
        self.assertArraysEqual(r.resized_array(), ['there', 'this is a longer line'])
        self.assertEqual(r.top_usable_row(), 3)

