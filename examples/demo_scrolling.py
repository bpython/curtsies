import sys
import signal

from curtsies.window import CursorAwareWindow
from curtsies import input
from curtsies.fmtstr import fmtstr

def cursor_winch():
    print 'this should be just off-screen'
    w = CursorAwareWindow(sys.stdout, sys.stdin, keep_last_line=True, hide_cursor=False)
    def sigwinch_handler(signum, frame):
        dy = w.get_cursor_vertical_diff()
        print 'sigwinch! Changed from %r to %r' % ((rows, columns), (w.height, w.width))
        print 'cursor moved %d lines down' % dy
        w.write(w.t.move_up)
        w.write(w.t.move_up)
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    with w:
        for e in input.Input():
            rows, columns = w.height, w.width
            a = [fmtstr((('.%sx%s.' % (rows, columns)) * rows)[:columns]) for row in range(rows)]
            w.render_to_terminal(a)
if __name__ == '__main__':
    cursor_winch()
