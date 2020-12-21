import unittest
import sys

from curtsies.window import BaseWindow, FullscreenWindow, CursorAwareWindow
from io import StringIO
from unittest import skipIf


fds_closed = not sys.stdin.isatty() or not sys.stdout.isatty()


class FakeFullscreenWindow(FullscreenWindow):
    width = property(lambda self: 10)
    height = property(lambda self: 4)


@skipIf(fds_closed, "blessings Terminal needs streams open")
class TestBaseWindow(unittest.TestCase):
    """Pretty pathetic tests for window"""

    def test_window(self):
        fakestdout = StringIO()
        window = BaseWindow(fakestdout)
        window.write("hi")
        fakestdout.seek(0)
        self.assertEqual(fakestdout.read(), "hi")

    def test_array_from_text(self):
        window = BaseWindow()
        a = window.array_from_text(".\n.\n.")
        self.assertEqual(a.height, 3)
        self.assertEqual(a[0], ".")
        self.assertEqual(a[1], ".")

    def test_array_from_text_rc(self):
        a = BaseWindow.array_from_text_rc("asdfe\nzx\n\n123", 3, 4)
        self.assertEqual(a.height, 3)
        self.assertEqual(a.width, 4)
        self.assertEqual(a[0], "asdf")
        self.assertEqual(a[1], "e")
        self.assertEqual(a[2], "zx")

    def test_fullscreen_window(self):
        fakestdout = StringIO()
        window = FullscreenWindow(fakestdout)
        window.write("hi")
        fakestdout.seek(0)
        self.assertEqual(fakestdout.read(), "hi")

    def test_fullscreen_render_to_terminal(self):
        fakestdout = StringIO()
        window = FakeFullscreenWindow(fakestdout)
        window.render_to_terminal(["hello", "hello", "hello"])
        fakestdout.seek(0)
        output = fakestdout.read()
        self.assertEqual(output.count("hello"), 3)
