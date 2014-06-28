# -*- coding: utf-8 -*-
import unittest
from curtsies.window import BaseWindow, FullscreenWindow, CursorAwareWindow
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

