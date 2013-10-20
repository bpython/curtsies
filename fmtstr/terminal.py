"""Terminal Wrapper which renders 2d arrays of characters to terminal"""

import sys
import os
import logging

from .fmtstr import fmtstr
from .fsarray import FSArray

from . import events


class Terminal(object):
    """ Renders 2D arrays of characters and cursor position """
    #TODO: when less than whole screen owned, deal with that:
    #    -render the top of the screen at the first clear row
    #    -scroll down before rendering as necessary
    def __init__(self, tc, keep_last_line=False, hide_cursor=True):
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
        logging.debug('-------initializing Terminal object %r------' % self)
        self.tc = tc
        self.keep_last_line = keep_last_line
        self.hide_cursor = hide_cursor
        self._last_lines_by_row = {}
        self._last_rendered_width = 0
        self._last_rendered_height = 0

    def __enter__(self):
        if self.hide_cursor:
            self.tc.hide_cursor()
        self.top_usable_row, _ = self.tc.get_cursor_position()
        logging.debug('initial top_usable_row: %d' % self.top_usable_row)
        return self

    def __exit__(self, type, value, traceback):
        logging.debug("running Terminal.__exit__")
        if self.keep_last_line:
            self.tc.scroll_down()
        row, _ = self.tc.get_cursor_position()
        self.tc.erase_rest_of_screen()
        self.tc.set_cursor_position((row, 1))
        self.tc.erase_rest_of_line()
        if self.hide_cursor:
            self.tc.show_cursor()

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
        height, width = self.tc.get_screen_size()
        if height != self._last_rendered_height or width != self._last_rendered_width:
            self._last_lines_by_row = {}
        self._last_rendered_width = width
        self._last_rendered_height = height
        current_lines_by_row = {}
        rows_for_use = list(range(self.top_usable_row, height + 1))
        shared = min(len(array), len(rows_for_use))
        for row, line in zip(rows_for_use[:shared], array[:shared]):
            current_lines_by_row[row] = line
            if line == self._last_lines_by_row.get(row, None):
                continue
            self.tc.set_cursor_position((row, 1))
            self.tc.write(str(line))
            if len(line) < width:
                self.tc.erase_rest_of_line()
        rest_of_lines = array[shared:]
        rest_of_rows = rows_for_use[shared:]
        for row in rest_of_rows: # if array too small
            if self._last_lines_by_row and row not in self._last_lines_by_row: continue
            self.tc.set_cursor_position((row, 1))
            self.tc.erase_line()
            current_lines_by_row[row] = None
        offscreen_scrolls = 0
        self.tc.set_cursor_position((height, 1)) # since scroll-down only moves the screen if cursor is at bottom
        for line in rest_of_lines: # if array too big
            logging.debug('sending scroll down message')
            self.tc.scroll_down()
            if self.top_usable_row > 1:
                self.top_usable_row -= 1
            else:
                offscreen_scrolls += 1
            current_lines_by_row = dict((k-1, v) for k, v in current_lines_by_row.items())
            logging.debug('new top_usable_row: %d' % self.top_usable_row)
            self.tc.set_cursor_position((height, 1)) # since scrolling moves the cursor
            self.tc.write(str(line))
            current_lines_by_row[height] = line

        logging.debug('lines in last lines by row: %r' % self._last_lines_by_row.keys())
        logging.debug('lines in current lines by row: %r' % current_lines_by_row.keys())
        self.tc.set_cursor_position((cursor_pos[0]-offscreen_scrolls+self.top_usable_row, cursor_pos[1]+1))
        self._last_lines_by_row = current_lines_by_row
        return offscreen_scrolls

    def array_from_text(self, msg):
        rows, columns = self.tc.get_screen_size()
        arr = FSArray(0, columns)
        i = 0
        for c in msg:
            if i >= rows * columns:
                return arr
            elif c in '\r\n':
                i = ((i // columns) + 1) * columns
            else:
                arr[i // arr.columns, i % arr.columns] = [fmtstr(c)]
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
                arr[i // arr.columns, i % arr.columns] = [fmtstr(c)]
            i += 1
        return arr

def test():
    from . import terminalcontrol
    with terminalcontrol.TerminalController(sys.stdin, sys.stdout) as tc:
        with Terminal(tc) as t:
            rows, columns = t.tc.get_screen_size()
            while True:
                c = t.tc.get_event()
                if c == "":
                    sys.exit() # same as raise SystemExit()
                elif c == "h":
                    a = t.array_from_text("a for small array")
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
                    a = t.array_from_text("window just changed to %d rows and %d columns" % (c.rows, c.columns))
                elif c == '\x0c': # ctrl-L
                    [t.tc.write('\n') for _ in range(rows)]
                    continue
                else:
                    a = t.array_from_text("unknown command")
                t.render_to_terminal(a)

def main():
    t = Terminal(sys.stdin, sys.stdout)
    rows, columns = t.tc.get_screen_size()
    import random
    goop = lambda l: [random.choice('aaabcddeeeefghiiijklmnooprssttuv        ') for _ in range(l)]
    a = [fmtstr(goop) for _ in range(rows)]
    t.render_to_terminal(a)
    while True:
        c = t.tc.get_event()
        if c == "":
            t.cleanup()
            sys.exit()
        t.render_to_terminal([fmtstr(c*columns) for _ in range(rows)])

def test_array_from_text():
    class FakeTC(object): get_screen_size = lambda self: (30, 50)
    t = Terminal(FakeTC())
    a = t.array_from_text('\n\nhey there\nyo')
    os.system('reset')
    for line in a:
        print(str(line))
    input()

if __name__ == '__main__':
    test_array_from_text()
    test()
