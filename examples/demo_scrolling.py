import sys
import signal

from curtsies import CursorAwareWindow, input, fmtstr

rows, columns = '??'
def cursor_winch():
    global rows, columns # instead of closure for Python 2 compatibility
    print('this should be just off-screen')
    w = CursorAwareWindow(sys.stdout, sys.stdin, keep_last_line=False, hide_cursor=False)
    def sigwinch_handler(signum, frame):
        global rows, columns
        dy = w.get_cursor_vertical_diff()
        old_rows, old_columns = rows, columns
        rows, columns = w.height, w.width
        print('sigwinch! Changed from %r to %r' % ((old_rows, old_columns), (rows, columns)))
        print('cursor moved %d lines down' % dy)
        w.write(w.t.move_up)
        w.write(w.t.move_up)
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    with w:
        for e in input.Input():
            rows, columns = w.height, w.width
            a = [fmtstr(((u'.%sx%s.' % (rows, columns)) * rows)[:columns]) for row in range(rows)]
            w.render_to_terminal(a)
            if e == u'<ESC>':
                break
if __name__ == '__main__':
    cursor_winch()
