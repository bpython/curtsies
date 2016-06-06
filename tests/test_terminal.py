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


# a few tests fail on TravisCI that have something to do with
# stdin not being able to be set to nonblocking
# (and still reporting isatty as True)
IS_TRAVIS = bool(os.environ.get("TRAVIS"))

try:
    from unittest import skipUnless, skipIf
except ImportError:
    def skipUnless(condition, reason):
        if condition:
            return lambda x: x
        else:
            return lambda x: None
    def skipIf(condition, reason):
        if condition:
            return lambda x: None
        else:
            return lambda x: x


class FakeStdin(StringIO):
    encoding = 'ascii'


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
        self._report_file = FakeStdin()
        super(ReportingScreen, self).__init__(*args, **kwargs)

    def report_cursor_position(self):
        # cursor position is 1-indexed in the ANSI escape sequence API
        s = ctrl.CSI + "%d;%sR" % (self.cursor.y + 1, self.cursor.x + 1)
        self._report_file.seek(0)
        self._report_file.write(s)
        self._report_file.seek(0)


class ReportingScreenWithExtra(ReportingScreen):
    def report_cursor_position(self):
        # cursor position is 1-indexed in the ANSI escape sequence API
        extra = 'qwerty\nasdf\nzxcv'
        s = ctrl.CSI + "%d;%sR" % (self.cursor.y + 1, self.cursor.x + 1)
        self._report_file.seek(0)
        self._report_file.write(extra + s)
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


@skipUnless(sys.stdin.isatty(), 'blessings Terminal needs streams open')
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


@skipIf(IS_TRAVIS, 'Travis stdin behaves strangely, see issue 89')
@skipUnless(sys.stdin.isatty(), 'blessings Terminal needs streams open')
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


@skipIf(IS_TRAVIS, 'Travis stdin behaves strangely, see issue 89')
@skipUnless(sys.stdin.isatty(), 'blessings Terminal needs streams open')
class TestCursorAwareWindowWithExtraInput(unittest.TestCase):
    def setUp(self):
        self.screen = ReportingScreenWithExtra(6, 3)
        self.stream = ReportingStream()
        self.stream.attach(self.screen)
        self.stream.attach(Bugger())
        stdout = ScreenStdout(self.stream)
        self.extra_bytes = []
        self.window = CursorAwareWindow(out_stream=stdout,
                                        in_stream=self.screen._report_file,
                                        extra_bytes_callback=self.extra_bytes_callback)
        self.window.cbreak = NopContext()
        blessings.Terminal.height = 3
        blessings.Terminal.width = 6

    def extra_bytes_callback(self, bytes):
        self.extra_bytes.append(bytes)

    def test_report_extra_bytes(self):
        with self.window:
            pass # should have triggered getting initial cursor position
        self.assertEqual(b''.join(self.extra_bytes), b'qwerty\nasdf\nzxcv')
