# All windows write only unicode to the terminal -
# that's what blessings does, so we match it.

from __future__ import unicode_literals

import locale
import logging
import re
import sys

import blessings

from .formatstring import fmtstr
from .formatstringarray import FSArray
from .termhelpers import Cbreak

logger = logging.getLogger(__name__)

SCROLL_DOWN = u"\x1bD"
FIRST_COLUMN = u"\x1b[1G"


class BaseWindow(object):
    def __init__(self, out_stream=None, hide_cursor=True):
        logger.debug('-------initializing Window object %r------' % self)
        if out_stream is None:
            out_stream = sys.__stdout__
        self.t = blessings.Terminal(stream=out_stream, force_styling=True)
        self.out_stream = out_stream
        self.hide_cursor = hide_cursor
        self._last_lines_by_row = {}
        self._last_rendered_width = None
        self._last_rendered_height = None

    def scroll_down(self):
        logger.debug('sending scroll down message w/ cursor on bottom line')

        # since scroll-down only moves the screen if cursor is at bottom
        with self.t.location(x=0, y=1000000):
            self.write(SCROLL_DOWN)  # TODO will blessings do this?

    def write(self, msg):
        self.out_stream.write(msg)
        self.out_stream.flush()

    def __enter__(self):
        logger.debug("running BaseWindow.__enter__")
        if self.hide_cursor:
            self.write(self.t.hide_cursor)
        return self

    def __exit__(self, type, value, traceback):
        logger.debug("running BaseWindow.__exit__")
        if self.hide_cursor:
            self.write(self.t.normal_cursor)

    def on_terminal_size_change(self, height, width):
        # Changing the terminal size breaks the cache, because it
        # is unknown how the window size change affected scrolling / the cursor
        self._last_lines_by_row = {}
        self._last_rendered_width = width
        self._last_rendered_height = height

    def render_to_terminal(self, array, cursor_pos=(0, 0)):
        raise NotImplemented

    def get_term_hw(self):
        """Returns current terminal height and width"""
        return self.t.height, self.t.width

    width = property(lambda self: self.t.width, None, None,
                     "The current width of the terminal window")
    height = property(lambda self: self.t.height, None, None,
                      "The current height of the terminal window")

    def array_from_text(self, msg):
        """Returns a FSArray of the size of the window containing msg"""
        rows, columns = self.t.height, self.t.width
        return self.array_from_text_rc(msg, rows, columns)

    @classmethod
    def array_from_text_rc(cls, msg, rows, columns):
        arr = FSArray(0, columns)
        i = 0
        for c in msg:
            if i >= rows * columns:
                return arr
            elif c in '\r\n':
                i = ((i // columns) + 1) * columns - 1
            else:
                arr[i // arr.width, i % arr.width] = [fmtstr(c)]
            i += 1
        return arr

    def fmtstr_to_stdout_xform(self):
        if sys.version_info[0] == 2:
            if hasattr(self.out_stream, 'encoding'):
                encoding = self.out_stream.encoding
            else:
                encoding = locale.getpreferredencoding()

            def for_stdout(s):
                return unicode(s).encode(encoding, 'replace')
        else:
            def for_stdout(s):
                return str(s)
        return for_stdout


class FullscreenWindow(BaseWindow):
    """2D-text rendering window that dissappears when its context is left

    FullscreenWindow will only render arrays the size of the terminal
    or smaller, and leaves no trace on exit (like top or vim). It never
    scrolls the terminal. Changing the terminal size doesn't do anything,
    but rendered arrays need to fit on the screen.

    Note:
        The context of the FullscreenWindow
        object must be entered before calling any of its methods.

        Within the context of CursorAwareWindow, refrain from writing to
        its out_stream; cached writes will be inaccurate.
    """
    def __init__(self, out_stream=None, hide_cursor=True):
        """Constructs a FullscreenWindow

        Args:
            out_stream (file): Defaults to sys.__stdout__
            hide_cursor (bool): Hides cursor while in context
        """
        BaseWindow.__init__(self, out_stream=out_stream,
                            hide_cursor=hide_cursor)
        self.fullscreen_ctx = self.t.fullscreen()

    def __enter__(self):
        self.fullscreen_ctx.__enter__()
        return BaseWindow.__enter__(self)

    def __exit__(self, type, value, traceback):
        self.fullscreen_ctx.__exit__(type, value, traceback)
        BaseWindow.__exit__(self, type, value, traceback)

    def render_to_terminal(self, array, cursor_pos=(0, 0)):
        """Renders array to terminal and places (0-indexed) cursor

        Args:
            array (FSArray): Grid of styled characters to be rendered.

        * If array received is of width too small, render it anyway
        * If array received is of width too large,
        * render the renderable portion
        * If array received is of height too small, render it anyway
        * If array received is of height too large,
        * render the renderable portion (no scroll)
        """
        # TODO there's a race condition here - these height and widths are
        # super fresh - they might change between the array being constructed
        # and rendered
        # Maybe the right behavior is to throw away the render
        # in the signal handler?
        height, width = self.height, self.width

        for_stdout = self.fmtstr_to_stdout_xform()
        if not self.hide_cursor:
            self.write(self.t.hide_cursor)
        if (height != self._last_rendered_height or
                width != self._last_rendered_width):
            self.on_terminal_size_change(height, width)

        current_lines_by_row = {}
        rows = list(range(height))
        rows_for_use = rows[:len(array)]
        rest_of_rows = rows[len(array):]

        # rows which we have content for and don't require scrolling
        for row, line in zip(rows_for_use, array):
            current_lines_by_row[row] = line
            if line == self._last_lines_by_row.get(row, None):
                continue
            self.write(self.t.move(row, 0))
            self.write(for_stdout(line))
            if len(line) < width:
                self.write(self.t.clear_eol)

        # rows onscreen that we don't have content for
        for row in rest_of_rows:
            if self._last_lines_by_row and row not in self._last_lines_by_row:
                continue
            self.write(self.t.move(row, 0))
            self.write(self.t.clear_eol)
            self.write(self.t.clear_bol)
            current_lines_by_row[row] = None

        logger.debug(
            'lines in last lines by row: %r' % self._last_lines_by_row.keys()
        )
        logger.debug(
            'lines in current lines by row: %r' % current_lines_by_row.keys()
        )
        self.write(self.t.move(*cursor_pos))
        self._last_lines_by_row = current_lines_by_row
        if not self.hide_cursor:
            self.write(self.t.normal_cursor)


class CursorAwareWindow(BaseWindow):
    """
    Renders to the normal terminal screen and
    can find the location of the cursor.

    Note:
        The context of the CursorAwareWindow
        object must be entered before calling any of its methods.

        Within the context of CursorAwareWindow, refrain from writing to
        its out_stream; cached writes will be inaccurate and calculating
        cursor depends on cursor not having moved since the last render.
        Only use the render_to_terminal interface for moving the cursor.
    """
    def __init__(self, out_stream=None, in_stream=None,
                 keep_last_line=False, hide_cursor=True,
                 extra_bytes_callback=None):
        """Constructs a CursorAwareWindow

        Args:
            out_stream (file): Defaults to sys.__stdout__
            in_stream (file): Defaults to sys.__stdin__
            keep_last_line (bool): Causes the cursor to be moved down one line
                on leaving context
            hide_cursor (bool): Hides cursor while in context
            extra_bytes_callback (f(bytes) -> None): Will be called with extra
                bytes inadvertantly read in get_cursor_position(). If not
                provided, a ValueError will be raised when this occurs.
        """
        BaseWindow.__init__(self, out_stream=out_stream,
                            hide_cursor=hide_cursor)
        if in_stream is None:
            in_stream = sys.__stdin__
        self.in_stream = in_stream
        self._last_cursor_column = None
        self._last_cursor_row = None
        self.keep_last_line = keep_last_line
        self.cbreak = Cbreak(self.in_stream)
        self.extra_bytes_callback = extra_bytes_callback

        # whether another SIGWINCH is queued up
        self.another_sigwinch = False

        # in the cursor query code of cursor diff
        self.in_get_cursor_diff = False

    def __enter__(self):
        self.cbreak.__enter__()
        self.top_usable_row, _ = self.get_cursor_position()
        self._orig_top_usable_row = self.top_usable_row
        logger.debug('initial top_usable_row: %d' % self.top_usable_row)
        return BaseWindow.__enter__(self)

    def __exit__(self, type, value, traceback):
        if self.keep_last_line:
            # just moves cursor down if not on last line
            self.write(SCROLL_DOWN)

        self.write(FIRST_COLUMN)
        self.write(self.t.clear_eos)
        self.write(self.t.clear_eol)
        self.cbreak.__exit__(type, value, traceback)
        BaseWindow.__exit__(self, type, value, traceback)

    def get_cursor_position(self):
        """Returns the terminal (row, column) of the cursor

        0-indexed, like blessings cursor positions"""
        # TODO would this be cleaner as a parameter?
        in_stream = self.in_stream

        query_cursor_position = u"\x1b[6n"
        self.write(query_cursor_position)

        def retrying_read():
            while True:
                try:
                    c = in_stream.read(1)
                    if c == '':
                        raise ValueError("Stream should be blocking - should't"
                                         " return ''. Returned %r so far",
                                         (resp,))
                    return c
                except IOError:
                    raise ValueError(
                        'cursor get pos response read interrupted'
                    )
                    # find out if this ever really happens - if so, continue

        resp = ''
        while True:
            c = retrying_read()
            resp += c
            m = re.search('(?P<extra>.*)'
                          '(?P<CSI>\x1b\[|\x9b)'
                          '(?P<row>\\d+);(?P<column>\\d+)R', resp, re.DOTALL)
            if m:
                row = int(m.groupdict()['row'])
                col = int(m.groupdict()['column'])
                extra = m.groupdict()['extra']
                if extra:
                    if self.extra_bytes_callback:
                        self.extra_bytes_callback(
                            extra.encode(in_stream.encoding)
                        )
                    else:
                        raise ValueError(("Bytes preceding cursor position "
                                          "query response thrown out:\n%r\n"
                                          "Pass an extra_bytes_callback to "
                                          "CursorAwareWindow to prevent this")
                                         % (extra,))
                return (row - 1, col - 1)

    def get_cursor_vertical_diff(self):
        """Returns the how far down the cursor moved since last render.

        Note:
            If another get_cursor_vertical_diff call is already in progress,
            immediately returns zero. (This situation is likely if
            get_cursor_vertical_diff is called from a SIGWINCH signal
            handler, since sigwinches can happen in rapid succession and
            terminal emulators seem not to respond to cursor position
            queries before the next sigwinch occurs.)
        """
        # Probably called by a SIGWINCH handler, and therefore
        # will do cursor querying until a SIGWINCH doesn't happen during
        # the query. Calls to the function from a signal handler COULD STILL
        # HAPPEN out of order -
        # they just can't interrupt the actual cursor query.
        if self.in_get_cursor_diff:
            self.another_sigwinch = True
            return 0

        cursor_dy = 0
        while True:
            self.in_get_cursor_diff = True
            self.another_sigwinch = False
            cursor_dy += self._get_cursor_vertical_diff_once()
            self.in_get_cursor_diff = False
            if not self.another_sigwinch:
                return cursor_dy

    def _get_cursor_vertical_diff_once(self):
        """Returns the how far down the cursor moved."""
        old_top_usable_row = self.top_usable_row
        row, col = self.get_cursor_position()
        if self._last_cursor_row is None:
            cursor_dy = 0
        else:
            cursor_dy = row - self._last_cursor_row
            logger.info('cursor moved %d lines down' % cursor_dy)
            while self.top_usable_row > -1 and cursor_dy > 0:
                self.top_usable_row += 1
                cursor_dy -= 1
            while self.top_usable_row > 1 and cursor_dy < 0:
                self.top_usable_row -= 1
                cursor_dy += 1
        logger.info('top usable row changed from %d to %d', old_top_usable_row,
                    self.top_usable_row)
        logger.info('returning cursor dy of %d from curtsies' % cursor_dy)
        self._last_cursor_row = row
        return cursor_dy

    def render_to_terminal(self, array, cursor_pos=(0, 0)):
        """Renders array to terminal, returns the number of lines scrolled offscreen

        Returns:
            Number of times scrolled

        Args:
          array (FSArray): Grid of styled characters to be rendered.

            If array received is of width too small, render it anyway

            if array received is of width too large, render it anyway

            if array received is of height too small, render it anyway

            if array received is of height too large, render it, scroll down,
            and render the rest of it, then return how much we scrolled down

        """
        for_stdout = self.fmtstr_to_stdout_xform()
        # caching of write and tc (avoiding the self. lookups etc) made
        # no significant performance difference here
        if not self.hide_cursor:
            self.write(self.t.hide_cursor)

        # TODO race condition here?
        height, width = self.t.height, self.t.width
        if (height != self._last_rendered_height or
                width != self._last_rendered_width):
            self.on_terminal_size_change(height, width)

        current_lines_by_row = {}
        rows_for_use = list(range(self.top_usable_row, height))

        # rows which we have content for and don't require scrolling
        # TODO rename shared
        shared = min(len(array), len(rows_for_use))
        for row, line in zip(rows_for_use[:shared], array[:shared]):
            current_lines_by_row[row] = line
            if line == self._last_lines_by_row.get(row, None):
                continue
            self.write(self.t.move(row, 0))
            self.write(for_stdout(line))
            if len(line) < width:
                self.write(self.t.clear_eol)

        # rows already on screen that we don't have content for
        rest_of_lines = array[shared:]
        rest_of_rows = rows_for_use[shared:]
        for row in rest_of_rows:  # if array too small
            if self._last_lines_by_row and row not in self._last_lines_by_row:
                continue
            self.write(self.t.move(row, 0))
            self.write(self.t.clear_eol)
            # TODO probably not necessary - is first char cleared?
            self.write(self.t.clear_bol)
            current_lines_by_row[row] = None

        # lines for which we need to scroll down to render
        offscreen_scrolls = 0
        for line in rest_of_lines:  # if array too big
            self.scroll_down()
            if self.top_usable_row > 0:
                self.top_usable_row -= 1
            else:
                offscreen_scrolls += 1
            current_lines_by_row = dict(
                (k - 1, v) for k, v in current_lines_by_row.items()
            )
            logger.debug('new top_usable_row: %d' % self.top_usable_row)
            # since scrolling moves the cursor
            self.write(self.t.move(height - 1, 0))
            self.write(for_stdout(line))
            current_lines_by_row[height - 1] = line

        logger.debug(
            'lines in last lines by row: %r' % self._last_lines_by_row.keys()
        )
        logger.debug(
            'lines in current lines by row: %r' % current_lines_by_row.keys()
        )
        self._last_cursor_row = max(
            0, cursor_pos[0] - offscreen_scrolls + self.top_usable_row
        )
        self._last_cursor_column = cursor_pos[1]
        self.write(
            self.t.move(self._last_cursor_row, self._last_cursor_column)
        )
        self._last_lines_by_row = current_lines_by_row
        if not self.hide_cursor:
            self.write(self.t.normal_cursor)
        return offscreen_scrolls


def demo():
    handler = logging.FileHandler(filename='display.log')
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(handler)
    from . import input
    with FullscreenWindow(sys.stdout) as w:
        with input.Input(sys.stdin) as input_generator:
            rows, columns = w.t.height, w.t.width
            while True:
                c = input_generator.next()
                if c == "":
                    sys.exit()  # same as raise SystemExit()
                elif c == "h":
                    a = w.array_from_text("a for small array")
                elif c == "a":
                    a = [fmtstr(c * columns) for _ in range(rows)]
                elif c == "s":
                    a = [fmtstr(c * columns) for _ in range(rows - 1)]
                elif c == "d":
                    a = [fmtstr(c * columns) for _ in range(rows + 1)]
                elif c == "f":
                    a = [fmtstr(c * columns) for _ in range(rows - 2)]
                elif c == "q":
                    a = [fmtstr(c * columns) for _ in range(1)]
                elif c == "w":
                    a = [fmtstr(c * columns) for _ in range(1)]
                elif c == "e":
                    a = [fmtstr(c * columns) for _ in range(1)]
                elif c == '\x0c':  # ctrl-L
                    [w.write('\n') for _ in range(rows)]
                    continue
                else:
                    a = w.array_from_text("unknown command")
                w.render_to_terminal(a)


def main():
    handler = logging.FileHandler(filename='display.log', level=logging.DEBUG)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(handler)
    print('this should be just off-screen')
    w = FullscreenWindow(sys.stdout)
    rows, columns = w.t.height, w.t.width
    with w:
        a = [fmtstr(
            (('.row%r.' % (row,)) * rows)[:columns]
        ) for row in range(rows)]
        w.render_to_terminal(a)

if __name__ == '__main__':
    demo()
