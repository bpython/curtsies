from __future__ import unicode_literals

import sys
import os
import unittest

try:
    from unittest import skip
except ImportError:
    def skip(f):
        return lambda self: None

if sys.version_info[0] == 3:
    from io import StringIO
else:
    from StringIO import StringIO

import blessings
import pyte
from pyte import control as ctrl, Stream, Screen, HistoryScreen
from pyte.screens import Margins

from curtsies.window import BaseWindow, FullscreenWindow, CursorAwareWindow
from curtsies.input import Input
from terminal_dsl import TestTerminalResizing

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

class ReportingScreen(HistoryScreen):
    def __init__(self, *args, **kwargs):
        self._report_file = StringIO()
        super(ReportingScreen, self).__init__(*args, **kwargs)

    def report_cursor_position(self):
        # cursor position is 1-indexed in the ANSI escape sequence API
        s = ctrl.CSI + "%d;%sR" % (self.cursor.y + 1, self.cursor.x + 1)
        self._report_file.seek(0)
        self._report_file.write(s)
        self._report_file.seek(0)

class HistoryPreservingOnResizeScreen(ReportingScreen):
    """Overriding resize to
    * preserve history that is pushed off screen
    * move cursor if necessary
    """
    #TODO: This is super hacky. It's been manipulated just enough
    #      to get the behavior I observe from xterm.
    #      Would be much better to find a proper implementation
    #      Cursor movement is wrong in edge cases, adding to history is less bad
    def resize(self, lines=None, columns=None):
        lines = lines or self.lines
        columns = columns or self.columns

        # First resize the lines:
        diff = self.lines - lines

        # a) if the current display size is less than the requested
        #    size, add lines to the bottom.
        if diff < 0:
            self.buffer.extend(take(self.columns, self.default_line)
                               for _ in range(diff, 0))
        # b) if the current display size is greater than requested
        #    size, take lines off the top.
        elif diff > 0:
            self.history.top.extend(self.buffer[:diff])
            self.buffer[:diff] = ()
            self.cursor.y -= diff

        # Then resize the columns:
        diff = self.columns - columns

        # a) if the current display size is less than the requested
        #    size, expand each line to the new size.
        if diff < 0:
            for y in range(lines):
                self.buffer[y].extend(take(abs(diff), self.default_line))
        # b) if the current display size is greater than requested
        #    size, trim each line from the right to the new size.
        elif diff > 0:
            for line in self.buffer:
                del line[columns:]

        self.lines, self.columns = lines, columns
        self.margins = Margins(0, self.lines - 1)
        old_x, old_y = self.cursor.x, self.cursor.y
        self.reset_mode(pyte.modes.DECOM)
        self.cursor.x = old_x
        self.cursor.y = old_y


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
        self.stream.feed(s)
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

class TestCursorAwareWindow(unittest.TestCase):
    def setUp(self):
        self.screen = ReportingScreen(6, 3)
        self.stream = ReportingStream()
        self.stream.attach(self.screen)
        self.stream.attach(Bugger())
        stdout = ScreenStdout(self.stream)
        self.window = CursorAwareWindow(out_stream=stdout,
                                        in_stream=self.screen._report_file)
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

class FakeBpythonRepl(object):
    def __init__(self, get_rows_cols):
        self.scrolled = 0
        self.num_lines_output = 1
        self._get_rows_cols = get_rows_cols

    def add_line(self):
        self.num_lines_output += 1

    def paint(self):
        a = []
        for row in range(self.num_lines_output)[self.scrolled:]:
            line = '-'.join(str(row) for _ in range(self.columns))[:self.columns]
            a.append(line)
        return a

    rows    = property(lambda self: self._get_rows_cols()[0])
    columns = property(lambda self: self._get_rows_cols()[1])


class TestCursorAwareWindowHistoryPreservation(unittest.TestCase):
    def setUp(self):
        self.screen = HistoryPreservingOnResizeScreen(6, 3)
        self.stream = ReportingStream()
        self.stream.attach(self.screen)
        self.stream.attach(Bugger())
        stdout = ScreenStdout(self.stream)
        self.window = CursorAwareWindow(out_stream=stdout,
                                        in_stream=self.screen._report_file)
        self.window.top_usable_row = 0

        blessings.Terminal.height = 3
        blessings.Terminal.width = 6

        self.repl = FakeBpythonRepl(lambda: (blessings.Terminal.height, blessings.Terminal.width))

    def history_lines(self):
        return [''.join(c.data for c in line) for line in self.screen.history.top]

    def render(self):
        a = self.repl.paint()
        self.repl.scrolled += self.window.render_to_terminal(a, (len(a) - 1, 0))

    def assertScreenMatches(self, display, row, col):
        self.assertEqual(len(display), len(self.screen.display))
        for row, expected in zip(self.screen.display, display):
            self.assertEqual(row, expected)

    def assertCursor(self, row, col):
        self.assertEqual((self.screen.cursor.x, self.screen.cursor.y), (col, row))

    def test_scroll(self):
        self.render()
        self.assertEqual(self.screen.display, [u'0-0-0-', u'      ', u'      '])
        self.repl.add_line()
        self.render()
        self.assertEqual(self.screen.display, [u'0-0-0-', u'1-1-1-', u'      '])
        self.repl.add_line()
        self.repl.add_line()
        self.render()
        self.assertEqual(self.screen.display, [u'1-1-1-', u'2-2-2-', u'3-3-3-'])
        self.assertEqual(self.history_lines(), [u'0-0-0-'])
        self.repl.add_line()
        self.repl.add_line()
        self.render()
        self.assertEqual(self.screen.display, [u'3-3-3-', u'4-4-4-', u'5-5-5-'])
        self.assertEqual(self.history_lines(), [u'0-0-0-', u'1-1-1-', u'2-2-2-'])

    #TODO: hack pyte Screen to throw out empty lines when scrolling up
    #      or find a better real xterm emulator
    @skip("pyte's behavior differs from xterm here")
    def test_change_window_height_with_space_at_bottom(self):
        self.render()
        self.assertCursor(row=1, col=0)
        self.screen.resize(2, 6)
        self.assertEqual(self.screen.display, [u'0-0-0-', u'      '])
        self.assertCursor(row=1, col=0)
        self.screen.resize(3, 6)
        self.assertEqual(self.screen.display, [u'0-0-0-'] + [u'      '] * 2)
        self.screen.resize(4, 6)
        self.assertEqual(self.screen.display, [u'0-0-0-'] + [u'      '] * 3)

    def test_change_window_height_with_no_space_at_bottom(self):
        self.repl.add_line()
        self.repl.add_line()
        self.render()
        self.screen.resize(2, 6)
        self.assertEqual(self.history_lines(), [u'0-0-0-'])
        self.assertEqual(self.screen.display, [u'1-1-1-', u'2-2-2-'])
        self.assertCursor(row=1, col=0)

class TestTestTerminalResizing(unittest.TestCase, TestTerminalResizing):
    def test_simple(self):
        self.actions = []
        self.assertResizeMatches("""
        +--+   +--+
        +--+   +--+
        |a |   |a |
        |b@|   |b@|
        +--+   +--+
        """)
        self.assertTrue(word +' called' in self.actions
                        for word in ['prepare_terminal', 'render', 'resize', 'check_output'])
    def prepare_terminal(self, rows, columns, history, visible, cursor):
        self.actions.append('prepare_terminal called')
    def render(self, array, cursor):
        self.actions.append('render called')
    def resize(self, rows, columns):
        self.actions.append('resize called')
    def check_output(self):
        self.actions.append('check_output called')

