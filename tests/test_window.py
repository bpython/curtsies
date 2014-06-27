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

    def test_fullscreen_window(self):
        fakestdout = StringIO()
        window = FullscreenWindow(fakestdout)
        window.write('hi')
        fakestdout.seek(0)
        self.assertEqual(fakestdout.read(), 'hi')
