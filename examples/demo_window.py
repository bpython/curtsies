import sys
import signal
import logging

from curtsies import input, fmtstr, events, FullscreenWindow, CursorAwareWindow
from curtsies import events

def array_size_test(window):
    """Tests arrays one row too small or too large"""
    with window as w:
        print('a displays a screen worth of input, s one line less, and d one line more')
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
                elif c == '<ESC>': # allows exit without keyboard interrupt
                    break
                elif c == '\x0c': # ctrl-L
                    [w.write('\n') for _ in range(rows)]
                    continue
                else:
                    a = w.array_from_text("unknown command")
                w.render_to_terminal(a)

if __name__ == '__main__':
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    array_size_test(FullscreenWindow(sys.stdout))

