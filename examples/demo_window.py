from curtsies import input
from curtsies.fmtstr import fmtstr
from curtsies import events
from curtsies.window import FullscreenWindow, CursorAwareWindow
import sys
import signal
import logging
from curtsies.termhelpers import Cbreak

def simple_fullscreen():
    print 'this should be just off-screen'
    w = FullscreenWindow(sys.stdout)
    rows, columns = w.height, w.width
    with w:
        a = [fmtstr((('.row%r.' % (row,)) * rows)[:columns]) for row in range(rows)]
        w.render_to_terminal(a)

def array_size_test(window):
    """Tests arrays one row to small or too large"""
    with window as w:
        with input.Input(sys.stdin) as input_generator:
            while True:
                c = input_generator.next()
                rows, columns = w.height, w.width
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
                elif c == "c":
                    w.write(w.t.move(w.t.height-1, 0))
                    w.scroll_down()
                elif isinstance(c, events.WindowChangeEvent):
                    a = w.array_from_text("window just changed to %d rows and %d columns" % (c.rows, c.columns))
                elif c == '\x0c': # ctrl-L
                    [w.write('\n') for _ in range(rows)]
                    continue
                else:
                    a = w.array_from_text("unknown command")
                w.render_to_terminal(a)

def fullscreen_winch():
    print 'this should be just off-screen'
    w = FullscreenWindow(sys.stdout)
    def sigwinch_handler(signum, frame):
        print 'sigwinch! Changed from %r to %r' % ((rows, columns), (w.height, w.width))
    with w:
        while True:
            rows, columns = w.height, w.width
            a = [fmtstr((('.%sx%s.' % (rows, columns)) * rows)[:columns]) for row in range(rows)]
            w.render_to_terminal(a)
            raw_input()

def fullscreen_winch_with_input():
    print 'this should be just off-screen'
    w = FullscreenWindow(sys.stdout)
    def sigwinch_handler(signum, frame):
        print 'sigwinch! Changed from %r to %r' % ((rows, columns), (w.height, w.width))
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    with w:
        for e in input.Input():
            rows, columns = w.height, w.width
            a = [fmtstr((('.%sx%s.' % (rows, columns)) * rows)[:columns]) for row in range(rows)]
            w.render_to_terminal(a)

def cursor_winch():
    print 'this should be just off-screen'
    w = CursorAwareWindow(sys.stdout, sys.stdin, keep_last_line=True, hide_cursor=False)
    def sigwinch_handler(signum, frame):
        print 'sigwinch! Changed from %r to %r' % ((rows, columns), (w.height, w.width))
        print 'cursor moved %d lines down' % w.get_cursor_vertical_diff()
        w.write(w.t.move_up)
        w.write(w.t.move_up)
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    with w:
        for e in input.Input():
            rows, columns = w.height, w.width
            a = [fmtstr((('.%sx%s.' % (rows, columns)) * rows)[:columns]) for row in range(rows)]
            w.render_to_terminal(a)

if __name__ == '__main__':
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    #simple_fullscreen()
    #array_size_test(FullscreenWindow(sys.stdout))
    #array_size_test(CursorAwareWindow(sys.stdout, sys.stdin, keep_last_line=True, hide_cursor=True))
    #fullscreen_winch()
    cursor_winch()

