"""Classes for buffered rendering of 2D arrays of (colored) characters to the terminal

Windows provide buffered rendering of 2d arrays of (colored) charactors.

FullscreenWindow will only render arrays the size of the terminal
or smaller, and leaves no trace on exit (like top or vim). It never
scrolls the terminal. Changing the terminal size doesn't do anything,
but 2d array rendered needs to fit on the screen.

CursorAwareWindow provides the ability to find the
location of the cursor, and allows scrolling.
Sigwinches can be annotated with how the terminal scroll changed
Changing the terminal size breaks the cache, because it
is unknown how the window size change affected scrolling / the cursor.
Leaving the context of the window deletes everything below the cursor
at the beginning of the its current line.
(use scroll_down() from the last rendered line if you want to save all history)
"""

import sys
import os
import logging

import blessings

from .fmtstr import fmtstr
from .fsarray import FSArray

from . import events

#BIG TODO!!! 
#TODO How to get cursor position? It's a thing we need!
# 
#
# Option 1: Window has a reference to the corresponding stdin
#           Maybe an input generator is instantiated just for the Window?
# Option 2: Window has a reference to an input generator -
#           these are always created in pairs
# Option 3: Input generator has a reference to Window instance
#           to notify it whenever this a cursur request happens
# 
# I think there are less issues if this only happens at the very
# beginning - but no, we need at all the time for nice sigwinch handling
# We have to reliable deal with this.
#
# If we use a context manager on sys.stdin that restores its original
# state, doing a read ourselves won't be too dangerous - but what
# if we read data that we weren't supposed to touch, buffered up before
# the cursor response we needed?

# Maybe you can't get a window without passing in an input generator
# (similar to the old tc method) - but this stinks!

# look at `ungetc` - we can push chars back onto the input stream
# is this safe? For now going to try a hack where we just lose whatever
# else we had to read before we find the response to the cursor query - 
# if ungetc works, should be easy to add
# It that ungetc would require compiling code to install - that's a bit of a barrier
# for something you want to install all the time like bpython

# get_annotated_event is also going to need to work differently -
# since now we're just doing handlers, get_annotated_event should
# be a utility function or something - it's not part of 
# Window or input generator

#
# How about Window.get_cursor_position(input_generator)
# (or Window.get_cursor_position(input_stream), in which case events might be lost)
#

# There should be two windows: one that is aware of the cursor position and scrolls,
# and a simple one that isn't.


class BaseWindow(object):
    """ Renders 2D arrays of characters and cursor position """
    def __init__(self, out_stream=sys.stdout, hide_cursor=True):
        """
        tc expected to have must have methods:
            get_cursor_position()
            get_screen_size() -> (row, col)
            set_cursor_position((row, column))
            write(msg)
            scroll_down()
            erase_line()
            down, up, left, back()
            get_event() -> 'c' | events.WindowChangeEvent(rows, columns)
        """
        logging.debug('-------initializing Window object %r------' % self)
        self.t = blessings.Terminal()
        self.out_stream = out_stream
        self.hide_cursor = hide_cursor
        self._last_lines_by_row = {}
        self._last_rendered_width = None
        self._last_rendered_height = None

    #TODO allow nice external access of width and height

    def scroll_down():
        SCROLL_DOWN = "D"
        self.write(SCROLL_DOWN) #TODO will blessings do this?

    def write(self, msg):
        logging.debug('writing %r' % msg)
        self.out_stream.write(msg)
        self.out_stream.flush()

    def __enter__(self):
        logging.debug("running BaseWindow.__enter__")
        if self.hide_cursor:
            self.write(self.t.hide_cursor)
        return self

    def __exit__(self, type, value, traceback):
        logging.debug("running BaseWindow.__exit__")
        if self.hide_cursor:
            self.write(self.t.normal_cursor)

    def on_terminal_size_change(self, height, width):
        self._last_lines_by_row = {}
        self._last_rendered_width = width
        self._last_rendered_height = height

    def render_to_terminal(self, array, cursor_pos=(0,0)):
        """Renders array to terminal"""
        raise NotImplemented

    def array_from_text(self, msg):
        rows, columns = self.t.height, self.t.width
        arr = FSArray(0, columns)
        i = 0
        for c in msg:
            if i >= rows * columns:
                return arr
            elif c in '\r\n':
                i = ((i // columns) + 1) * columns
            else:
                arr[i // arr.width, i % arr.width] = [fmtstr(c)]
            i += 1
        return arr

    @classmethod
    def array_from_text_rc(cls, msg, rows, columns):
        arr = FSArray(0, columns)
        i = 0
        for c in msg:
            if i >= rows * columns:
                return arr
            elif c in '\r\n':
                i = ((i // columns) + 1) * columns
            else:
                arr[i // arr.width, i % arr.width] = [fmtstr(c)]
            i += 1
        return arr

class FullscreenWindow(BaseWindow):
    """A 2d-text rendering window that dissappears when its context is left

    Uses blessings's fullscreen capabilities"""
    def __init__(self, out_stream=sys.stdout, hide_cursor=True):
        BaseWindow.__init__(self, out_stream=out_stream, hide_cursor=hide_cursor)
        self.fullscreen_ctx = self.t.fullscreen()

    def __enter__(self):
        self.fullscreen_ctx.__enter__()
        return BaseWindow.__enter__(self)

    def __exit__(self, type, value, traceback):
        self.fullscreen_ctx.__exit__(type, value, traceback)
        BaseWindow.__exit__(self, type, value, traceback)

    def render_to_terminal(self, array, cursor_pos=(0,0)):
        """Renders array to terminal and places (0-indexed) cursor

        If array received is of width too small, render it anyway
        if array received is of width too large, render the renderable portion
        if array received is of height too small, render it anyway
        if array received is of height too large, render the renderable portion (no scroll)
        """
        #TODO there's a race condition here - these height and widths are
        # super fresh - they might change between the array being constructed and rendered
        # Maybe the right behavior is to throw away the render in the signal handler?
        height, width = self.t.height, self.t.width

        if not self.hide_cursor:
            self.write(self.t.hide_cursor)
        if height != self._last_rendered_height or width != self._last_rendered_width:
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
            self.write(str(line))
            if len(line) < width:
                self.write(self.t.clear_eol)

        # rows onscreen that we don't have content for
        for row in rest_of_rows:
            if self._last_lines_by_row and row not in self._last_lines_by_row: continue
            self.write(self.t.move(row, 0))
            self.write(self.t.clear_eol)
            self.write(self.t.clear_bol)
            current_lines_by_row[row] = None

        logging.debug('lines in last lines by row: %r' % self._last_lines_by_row.keys())
        logging.debug('lines in current lines by row: %r' % current_lines_by_row.keys())
        self.write(self.t.move(*cursor_pos))
        self._last_lines_by_row = current_lines_by_row
        if not self.hide_cursor:
            self.write(self.t.normal_cursor)

class CursorAwareWindow(BaseWindow):
    def __init__(self, out_stream=sys.stdout, keep_last_line=False, hide_cursor=True):
        BaseWindow.__init__(self, out_stream=out_stream, hide_cursor=hide_cursor)
        self._last_cursor_column = None
        self._last_cursor_row = None
        self.keep_last_line = keep_last_line

    def __enter__(self):
        self.top_usable_row, _ = self.get_cursor_position()
        self._orig_top_usable_row = self.top_usable_row
        logging.debug('initial top_usable_row: %d' % self.top_usable_row)

    def __exit__(self, type, value, traceback):
        row, _ = self.get_cursor_position()
        self.write(self.t.clear_eos)
        self.write(self.t.move(row, 0))
        self.write(self.t.clear_eol)

    def get_cursor_position(self, in_stream):
        """Returns the terminal (row, column) of the cursor"""
        QUERY_CURSOR_POSITION = "\x1b[6n"
        self.write(QUERY_CURSOR_POSITION)

        def retrying_read():
            while True:
                try:
                    return in_stream.read(1)
                except IOError:
                    raise ValueError('cursor get pos response read interrupted')
                    # to find out if this ever really happens
                    logging.debug('read interrupted, retrying')

        resp = ''
        while True:
            c = retrying_read()
            resp += c
            m = re.search('(?P<extra>.*)\x1b\[(?P<row>\\d+);(?P<column>\\d+)R', resp)
            if m:
                row = int(m.groupdict()['row'])
                col = int(m.groupdict()['column'])
                extra = m.groupdict()['extra']
                if extra:
                    raise ValueError("Whoops! chars preceding cursor pos query response thrown out! %r" % (extra,))
                return (row, col)

    def get_annotated_event(self, keynames='curses', idle=()):
        """get_event from self.tc, but add cursor_dy to window change events"""
        e = self.tc.get_event(keynames=keynames, idle=idle)
        if isinstance(e, events.WindowChangeEvent):
            row, col = self.get_cursor_position()
            if self._last_cursor_row is None:
                e.cursor_dy = 0
            else:
                e.cursor_dy = row - self._last_cursor_row
                while self.top_usable_row > 1 and e.cursor_dy > 0:
                    self.top_usable_row += 1
                    e.cursor_dy -= 1
                while self.top_usable_row > 1 and e.cursor_dy < 0:
                    self.top_usable_row -= 1
                    e.cursor_dy += 1
        return e

    def render_to_terminal(self, array, cursor_pos=(0,0)):
        """Renders array to terminal, returns the number of lines
            scrolled offscreen
        outputs:
         -number of times scrolled

        If array received is of width too small, render it anyway
        if array received is of width too large, render it anyway
        if array received is of height too small, render it anyway
        if array received is of height too large, render it, scroll down,
            and render the rest of it, then return how much we scrolled down
        """
        # caching of write and tc (avoiding the self. lookups etc) made
        # no significant performance difference here
        if not self.hide_cursor:
            self.write(self.t.hide_cursor)
        height, width = self.t.height, self.t.width
        if height != self._last_rendered_height or width != self._last_rendered_width:
            self.on_terminal_size_change(height, width)

        current_lines_by_row = {}
        rows_for_use = list(range(self.top_usable_row, height + 1))

        # rows which we have content for and don't require scrolling
        shared = min(len(array), len(rows_for_use)) #TODO rename shared
        for row, line in zip(rows_for_use[:shared], array[:shared]):
            current_lines_by_row[row] = line
            if line == self._last_lines_by_row.get(row, None):
                continue
            self.write(self.t.move(row, 1))
            self.write(str(line))
            if len(line) < width:
                self.write(self.t.clear_eol)

        # rows already on screen that we don't have content for
        rest_of_lines = array[shared:]
        rest_of_rows = rows_for_use[shared:]
        for row in rest_of_rows: # if array too small
            if self._last_lines_by_row and row not in self._last_lines_by_row: continue
            self.write(self.t.move(row, 1))
            self.write(self.t.clear_eol)
            self.write(self.t.clear_bol)
            current_lines_by_row[row] = None
        offscreen_scrolls = 0
        self.t.move(height, 1) # since scroll-down only moves the screen if cursor is at bottom

        # lines for which we need to scroll down to render
        for line in rest_of_lines: # if array too big
            logging.debug('sending scroll down message')
            self.scroll_down()
            if self.top_usable_row > 1:
                self.top_usable_row -= 1
            else:
                offscreen_scrolls += 1
            current_lines_by_row = dict((k-1, v) for k, v in current_lines_by_row.items())
            logging.debug('new top_usable_row: %d' % self.top_usable_row)
            self.t.move(height, 1) # since scrolling moves the cursor
            self.t.write(str(line))
            current_lines_by_row[height] = line

        logging.debug('lines in last lines by row: %r' % self._last_lines_by_row.keys())
        logging.debug('lines in current lines by row: %r' % current_lines_by_row.keys())
        self.write(self.t.move(cursor_pos[0]-offscreen_scrolls+self.top_usable_row), cursor_pos[1] + 1)
        self._last_cursor_row, self._last_cursor_column = (
                                    (cursor_pos[0]-offscreen_scrolls+self.top_usable_row, cursor_pos[1]+1))
        self._last_lines_by_row = current_lines_by_row
        if not self.hide_cursor:
            self.write(self.t.normal_cursor)
        return offscreen_scrolls


def test():
    import input
    with FullscreenWindow(sys.stdout) as w:
        with input.Input(sys.stdin) as input_generator:
            rows, columns = w.t.height, w.t.width
            while True:
                c = input_generator.next()
                if c == "":
                    sys.exit() # same as raise SystemExit()
                elif c == "h":
                    a = w.array_from_text("a for small array")
                elif c == "a":
                    a = [fmtstr(c*columns) for _ in range(rows)]
                elif c == "s":
                    a = [fmtstr(c*columns) for _ in range(rows-1)]
                elif c == "d":
                    a = [fmtstr(c*columns) for _ in range(rows+1)]
                elif c == "f":
                    a = [fmtstr(c*columns) for _ in range(rows-2)]
                elif c == "q":
                    a = [fmtstr(c*columns) for _ in range(1)]
                elif c == "w":
                    a = [fmtstr(c*columns) for _ in range(1)]
                elif c == "e":
                    a = [fmtstr(c*columns) for _ in range(1)]
                elif isinstance(c, events.WindowChangeEvent):
                    a = w.array_from_text("window just changed to %d rows and %d columns" % (c.rows, c.columns))
                elif c == '\x0c': # ctrl-L
                    [w.write('\n') for _ in range(rows)]
                    continue
                else:
                    a = w.array_from_text("unknown command")
                w.render_to_terminal(a)

def main():
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    from termhelpers import Cbreak
    print 'this should be just off-screen'
    w = FullscreenWindow(sys.stdout)
    rows, columns = w.t.height, w.t.width
    with w:
        a = [fmtstr((('.row%r.' % (row,)) * rows)[:columns]) for row in range(rows)]
        w.render_to_terminal(a)

if __name__ == '__main__':
    test()
