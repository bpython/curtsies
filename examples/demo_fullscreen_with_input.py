import sys
import signal

from curtsies import input, Cbreak, FullscreenWindow, fmtstr

def fullscreen_winch_with_input():
    print('this should be just off-screen')
    w = FullscreenWindow(sys.stdout)
    def sigwinch_handler(signum, frame):
        print('sigwinch! Changed from %r to %r' % ((rows, columns), (w.height, w.width)))
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    with w:
        with Cbreak(sys.stdin):
            for e in input.Input():
                rows, columns = w.height, w.width
                a = [fmtstr((('.%sx%s.%r.' % (rows, columns, e)) * rows)[:columns]) for row in range(rows)]
                w.render_to_terminal(a)

if __name__ == '__main__':
    fullscreen_winch_with_input()

