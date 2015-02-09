from __future__ import unicode_literals

import locale
import os
import sys
import unittest

if sys.version_info[0] == 3:
    from io import StringIO
else:
    from StringIO import StringIO

import blessings
import pyte
from pyte import control as ctrl, Stream, Screen

from curtsies.window import BaseWindow, FullscreenWindow, CursorAwareWindow

# thanks superbobry for this code: https://github.com/selectel/pyte/issues/13
class ReportingStream(Stream):
    report_escape = {
        "6": "report_cursor_position"
    }

    def _arguments(self, char):
        if char == "n":
            # DSR command looks like 'CSI<N>n'. So all we need to do
            # is wait for the 'n' argument.
            return self.dispatch(self.report_escape[self.current])
        else:
            return super(ReportingStream, self)._arguments(char)

class ReportingScreen(Screen):
    def __init__(self, *args, **kwargs):
        self._report_file = StringIO()
        super(ReportingScreen, self).__init__(*args, **kwargs)

    def report_cursor_position(self):
        # cursor position is 1-indexed in the ANSI escape sequence API
        s = ctrl.CSI + "%d;%sR" % (self.cursor.y + 1, self.cursor.x + 1)
        self._report_file.seek(0)
        self._report_file.write(s)
        self._report_file.seek(0)

class Bugger(object):
    __before__ = __after__ = lambda *args: None

    def __getattr__(self, event):
        to = sys.stdout
        def inner(*args, **flags):
            to.write(event.upper() + " ")
            to.write("; ".join(map(repr, args)))
            to.write(" ")
            to.write(", ".join("{0}: {1}".format(name, repr(arg))
                               for name, arg in flags.items()))
            to.write(os.linesep)
        return inner

class ScreenStdout(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, s):
        if sys.version_info[0] == 3:
            self.stream.feed(s)
        else:
            self.stream.feed(s.decode(locale.getpreferredencoding()))
    def flush(self): pass

class TestFullscreenWindow(unittest.TestCase):
    def setUp(self):
        self.screen = pyte.Screen(10, 3)
        self.stream = pyte.Stream()
        self.stream.attach(self.screen)
        stdout = ScreenStdout(self.stream)
        self.window = FullscreenWindow(stdout)

    def test_render(self):
        with self.window:
            self.window.render_to_terminal([u'hi', u'there'])
        self.assertEqual(self.screen.display, [u'hi        ', u'there     ', u'          '])

    def test_scroll(self):
        with self.window:
            self.window.render_to_terminal([u'hi', u'there'])
            self.window.scroll_down()
        self.assertEqual(self.screen.display, [u'there     ', u'          ', u'          '])

class NopContext(object):
    def __enter__(*args): pass
    def __exit__(*args): pass

class TestCursorAwareWindow(unittest.TestCase):
    def setUp(self):
        self.screen = ReportingScreen(6, 3)
        self.stream = ReportingStream()
        self.stream.attach(self.screen)
        self.stream.attach(Bugger())
        stdout = ScreenStdout(self.stream)
        self.window = CursorAwareWindow(out_stream=stdout,
                                        in_stream=self.screen._report_file)
        self.window.cbreak = NopContext()
        blessings.Terminal.height = 3
        blessings.Terminal.width = 6

    def test_render(self):
        with self.window:
            self.assertEqual(self.window.top_usable_row, 0)
            self.window.render_to_terminal([u'hi', u'there'])
            self.assertEqual(self.screen.display, [u'hi    ', u'there ', u'      '])

    def test_cursor_position(self):
        with self.window:
            self.window.render_to_terminal([u'hi', u'there'], cursor_pos=(2, 4))
            self.assertEqual(self.window.get_cursor_position(), (2, 4))

    def test_inital_cursor_position(self):

        self.screen.cursor.y += 1
        with self.window:
            self.assertEqual(self.window.top_usable_row, 1)
            self.window.render_to_terminal([u'hi', u'there'])
            self.assertEqual(self.screen.display, [u'      ', u'hi    ', u'there '])

